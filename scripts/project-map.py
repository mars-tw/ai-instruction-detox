#!/usr/bin/env python3
"""Validate explicit project routes and render new navigation files (stdlib only).

This program never executes a manifest value or reads the contents of route files.
Python 3.8+; see references/project-organization.md for the manifest contract.
"""

import argparse
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
from urllib.parse import quote
from locale_data import LANGUAGES, LocalizedParser, language_from_args, text as tr, translate_error


MAX_BYTES = 1024 * 1024
MAX_NODES = 500
ID_RE = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
BLOCKED_PARTS = {
    ".git", ".ssh", ".secrets", ".aws", ".gnupg", ".azure", "secrets", "credentials",
    "node_modules", "vendor", "dist", "build", "cache", "__pycache__", "models",
    "coverage", ".venv", "venv", ".pytest_cache", "ms-playwright",
}
BLOCKED_FILES = {"credentials.md", "credentials.json", "credentials.toml", "credentials.yaml",
                 "credentials.yml", "secrets.json", "secrets.yaml", "secrets.yml", ".netrc",
                 "_netrc", ".npmrc", ".pypirc", "id_rsa", "id_ed25519", "id_ecdsa",
                 "id_dsa", "authorized_keys", "known_hosts"}
BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".p8", ".keystore"}
RESERVED_RE = re.compile(r"(?:con|prn|aux|nul|clock\$|com[0-9]|lpt[0-9])(?:\.|$)", re.I)
FILES = ("project-map.md", "project-tree.txt", "project-mindmap.mmd",
         "project-dependencies.mmd")


class MapError(ValueError):
    """A manifest or filesystem route is unsafe or malformed."""


def error(message):
    raise MapError(message)


def exact_fields(value, required, label):
    if not isinstance(value, dict):
        error("{} must be an object".format(label))
    missing = set(required) - set(value)
    unknown = set(value) - set(required)
    if missing or unknown:
        # Keys are untrusted: never echo their contents into terminal diagnostics.
        error("{} has missing or unknown fields".format(label))


def clean_text(value, label, limit=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        error("{} must be a nonempty string (at most {} characters)".format(label, limit))
    if any(unicodedata.category(c) in ("Cc", "Cf", "Cs", "Zl", "Zp") for c in value):
        error("{} contains control, surrogate or formatting characters".format(label))
    return value


def identifier(value, label):
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        error("{} must match [a-z][a-z0-9-]{{0,63}}".format(label))
    return value


def route(value, label, allow_root=False):
    if allow_root and value == ".":
        return value
    clean_text(value, label, 1024)
    if any(c in value for c in '\\:%<>"|?*') or value.startswith("/"):
        error("{} must be a plain project-relative POSIX path".format(label))
    parts = value.split("/")
    for part in parts:
        if not part or part in (".", "..") or part.endswith((" ", ".")):
            error("{} contains an empty, traversal or ambiguous segment".format(label))
        if RESERVED_RE.match(part):
            error("{} contains a reserved device name".format(label))
        if excluded_part(part):
            error("{} points to an excluded or sensitive path".format(label))
    return value


def excluded_part(part):
    folded = part.casefold()
    return (folded in BLOCKED_PARTS or folded in BLOCKED_FILES
            or folded in (".env", ".envrc") or folded.startswith(".env.")
            or folded.startswith("credentials.")
            or PurePosixPath(part).suffix.casefold() in BLOCKED_SUFFIXES)


def is_link(metadata):
    return (stat.S_ISLNK(metadata.st_mode)
            or bool(getattr(metadata, "st_file_attributes", 0) & 0x400))


def inspect_path(path, expect=None, required=False):
    """lstat every ancestor; refuse symlinks and all Windows reparse points."""
    path = Path(os.path.abspath(str(path)))
    chain = list(reversed(path.parents)) + [path]
    present = False
    for index, component in enumerate(chain):
        try:
            metadata = component.lstat()
        except FileNotFoundError:
            if required:
                error("a required declared path does not exist")
            return False
        if is_link(metadata):
            error("a declared path or its parent is a symlink, junction or reparse point")
        leaf = index == len(chain) - 1
        if not leaf and not stat.S_ISDIR(metadata.st_mode):
            error("a declared path has a non-directory parent")
        if leaf:
            present = True
            if expect == "file" and not stat.S_ISREG(metadata.st_mode):
                error("a declared file path is not a regular file")
            if expect == "directory" and not stat.S_ISDIR(metadata.st_mode):
                error("a declared directory path is not a directory")
    return present


def project_root(value):
    clean_text(value, "project root", 4096)
    if value.startswith(("\\\\", "//")):
        error("network-share roots are refused")
    root = Path(os.path.abspath(value))
    if root.parent == root or os.path.normcase(str(root)) == os.path.normcase(os.path.abspath(os.path.expanduser("~"))):
        error("home and filesystem-root scopes are refused")
    if any(excluded_part(part) for part in root.parts):
        error("project root has an excluded or sensitive ancestor")
    inspect_path(root, "directory", required=True)
    return root


def beneath(child, parent):
    if parent == ".":
        return child != "."
    child_parts = PurePosixPath(child).parts
    parent_parts = PurePosixPath(parent).parts
    return (len(child_parts) > len(parent_parts)
            and child_parts[:len(parent_parts)] == parent_parts)


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            error("manifest contains duplicate JSON keys")
        result[key] = value
    return result


def load_manifest(root, relative):
    route(relative, "manifest")
    path = root / relative
    inspect_path(path, "file", required=True)
    # Avoid following a replaced final symlink where the host supports O_NOFOLLOW.
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    descriptor = os.open(str(path), flags)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            error("manifest is not a regular file")
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        error("manifest exceeds 1 MiB")
    try:
        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=no_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        error("manifest must be valid UTF-8 JSON without excessive nesting")


def validate_manifest(data, root, require_files=False):
    exact_fields(data, ("schema_version", "project", "subprojects"), "manifest")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        error("schema_version must be integer 1")
    project = data["project"]
    exact_fields(project, ("id", "name", "root", "main_skill", "workflow", "owner", "purpose", "sources"), "project")
    if project["root"] != ".":
        error("project.root must be '.'; the CLI --root sets the allowed directory")
    children = data["subprojects"]
    if not isinstance(children, list) or len(children) >= MAX_NODES:
        error("subprojects must be an array with fewer than {} items".format(MAX_NODES))
    # Normalize into fresh nodes without altering the source manifest.
    nodes = [dict(project, path=".", skill=project["main_skill"], parent=None, dependencies=[])]
    for child in children:
        exact_fields(child, ("id", "name", "parent", "path", "skill", "workflow", "owner", "purpose", "sources", "dependencies"), "subproject")
        nodes.append(dict(child))
    by_id = {}
    paths = set()
    governance = set()
    missing = []
    for node in nodes:
        identifier(node["id"], "node.id")
        if node["id"] in by_id:
            error("node IDs must be unique")
        by_id[node["id"]] = node
        for field in ("name", "owner", "purpose"):
            clean_text(node[field], "node." + field)
        route(node["path"], "node.path", allow_root=True)
        if node["path"].casefold() in paths:
            error("node paths must be unique, including case-insensitive matches")
        paths.add(node["path"].casefold())
        inspect_path(root / node["path"], "directory", required=True)
        for field in ("skill", "workflow"):
            route(node[field], "node." + field)
            if not beneath(node[field], node["path"]):
                error("skill and workflow paths must be within their owning node")
            if node[field].casefold() in governance:
                error("skill and workflow file paths must be unique")
            governance.add(node[field].casefold())
            if not inspect_path(root / node[field], "file", required=require_files):
                missing.append(node[field])
        sources = node["sources"]
        if not isinstance(sources, list) or not sources or len(sources) > 100:
            error("node.sources must be a nonempty array with at most 100 paths")
        seen_sources = set()
        for source in sources:
            route(source, "node.sources entry")
            if not beneath(source, node["path"]):
                error("source paths must be within their owning node")
            if source.casefold() in seen_sources:
                error("source paths must not repeat within a node")
            seen_sources.add(source.casefold())
            inspect_path(root / source, "file", required=True)
        dependencies = node["dependencies"]
        if not isinstance(dependencies, list) or len(dependencies) > MAX_NODES:
            error("node.dependencies must be an array of node IDs")
        for dependency in dependencies:
            identifier(dependency, "node.dependencies entry")
        if len(set(dependencies)) != len(dependencies):
            error("node dependencies must not repeat")
        if node["parent"] is not None:
            identifier(node["parent"], "node.parent")
        elif node is not nodes[0]:
            error("every subproject must declare a parent ID")
    root_id = nodes[0]["id"]
    for node in nodes[1:]:
        if node["parent"] not in by_id:
            error("node.parent refers to an unknown ID")
        if not beneath(node["path"], by_id[node["parent"]]["path"]):
            error("child paths must be strictly inside their parent path")
    for node in nodes:
        chain = set()
        cursor = node
        while cursor["parent"] is not None:
            if cursor["id"] in chain:
                error("parent relationships contain a cycle")
            chain.add(cursor["id"])
            cursor = by_id[cursor["parent"]]
        if cursor["id"] != root_id:
            error("every node must descend from the project root")
        for dependency in node["dependencies"]:
            if dependency not in by_id or dependency == node["id"]:
                error("dependencies must name known IDs other than the node itself")
    # A workflow dependency cycle is an unresolved design decision, not a route.
    states = {}
    def visit(node_id):
        if states.get(node_id) == 1:
            error("workflow dependencies contain a cycle")
        if states.get(node_id) == 2:
            return
        states[node_id] = 1
        for dependency in sorted(by_id[node_id]["dependencies"]):
            visit(dependency)
        states[node_id] = 2
    for node_id in sorted(by_id):
        visit(node_id)
    return nodes, sorted(missing)


def md_text(value):
    value = html.escape(value, quote=True)
    for character in r"\`*_[]{}()|#~":
        value = value.replace(character, "\\" + character)
    return value


def mermaid_text(value):
    # Entity-encode syntax and HTML punctuation while keeping labels readable.
    return "".join("&#{};".format(ord(c)) if c in '&<>"[]{}()\\`' else c for c in value)


def mermaid_id(value):
    # Prefix valid manifest IDs so values such as 'end' cannot become keywords.
    return "node_" + value.replace("-", "_")


def render_navigation(nodes, root, destination, missing, language="zh-TW"):
    by_id = {node["id"]: node for node in nodes}
    children = {node["id"]: [] for node in nodes}
    for node in nodes[1:]:
        children[node["parent"]].append(node["id"])
    for values in children.values():
        values.sort()
    ordered = []
    def walk(node_id, depth):
        ordered.append((by_id[node_id], depth))
        for child_id in children[node_id]:
            walk(child_id, depth + 1)
    walk(nodes[0]["id"], 0)
    def file_link(value):
        relative = os.path.relpath(str(root / value), str(destination)).replace(os.sep, "/")
        return quote(relative, safe="/-._~")
    markdown = ["# " + tr("navigation", language), "", tr("nav_intro", language), ""]
    status = tr("nav_all", language) if not missing else tr("nav_missing", language, count=len(missing))
    markdown += [tr("nav_status", language, status=status), ""]
    markdown += ["## " + tr("route_index", language), ""]
    for node, depth in ordered:
        markdown.append("{}- [{}](#node-{})".format("  " * depth, md_text(node["name"]), node["id"]))
    markdown.append("")
    tree = []
    mindmap = ["mindmap"]
    dependencies = ["flowchart LR"]
    for node, depth in ordered:
        tree.append("{}{} [{}] ({})".format("  " * depth, md_text(node["name"]), node["id"], node["path"]))
        mindmap.append('{}{}["{}"]'.format("  " * (depth + 1), mermaid_id(node["id"]), mermaid_text(node["name"])))
        dependencies.append('  {}["{}"]'.format(mermaid_id(node["id"]), mermaid_text(node["name"])))
        lineage = []
        cursor = node
        while cursor is not None:
            lineage.append(cursor)
            cursor = by_id[cursor["parent"]] if cursor["parent"] else None
        breadcrumb = " › ".join("[{}](#node-{})".format(md_text(part["name"]), part["id"]) for part in reversed(lineage))
        markdown += ['<a id="node-{}"></a>'.format(node["id"]), "", "## " + md_text(node["name"]), "", breadcrumb, ""]
        for field, label in (("path", "path"), ("owner", "owner"), ("purpose", "purpose")):
            markdown.append("- " + tr(label, language) + ": " + md_text(node[field]))
        for field, label in (("skill", "skill"), ("workflow", "workflow")):
            suffix = tr("not_created", language) if node[field] in missing else ""
            markdown.append("- {}: [{}]({}){}".format(tr(label, language), md_text(node[field]), file_link(node[field]), suffix))
        if node["dependencies"]:
            markdown.append("- " + tr("dependencies", language) + ": " + (", " if language in ("en", "de") else "、").join("[{}](#node-{})".format(md_text(by_id[item]["name"]), item) for item in sorted(node["dependencies"])))
        else:
            markdown.append("- " + tr("dependencies", language) + ": " + tr("none_declared", language))
        markdown.append("- " + tr("sources", language) + ": " + (", " if language in ("en", "de") else "、").join("[{}]({})".format(md_text(source), file_link(source)) for source in sorted(node["sources"])))
        markdown.append("")
        for dependency in sorted(node["dependencies"]):
            dependencies.append("  {} --> {}".format(mermaid_id(dependency), mermaid_id(node["id"])))
    markdown += ["## " + tr("maintenance", language), "", tr("nav_loading", language), "", tr("nav_derivation", language), ""]
    # Include diagrams in the clickable Markdown entry and standalone files;
    # all views still derive from the same manifest.
    markdown += ["## " + tr("tree", language), "", "```text"] + tree + ["```", "",
                 "## " + tr("mindmap", language), "", "```mermaid"] + mindmap + ["```", "",
                 "## " + tr("dependency_graph", language), "", "```mermaid"] + dependencies + ["```", ""]
    return dict(zip(FILES, ("\n".join(markdown), "\n".join(tree) + "\n", "\n".join(mindmap) + "\n", "\n".join(dependencies) + "\n")))


def write_new_outputs(root, relative, contents):
    route(relative, "output directory")
    destination = root / relative
    inspect_path(destination.parent, "directory", required=True)
    if inspect_path(destination, "directory"):
        error("output directory already exists; choose a new explicit destination")
    # No recursive mkdir: the user chooses an existing parent and a new leaf.
    os.mkdir(str(destination))
    created = []
    try:
        for filename in FILES:
            inspect_path(destination, "directory", required=True)
            path = destination / filename
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(str(path), flags, 0o600)
            created.append(path)
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(contents[filename])
    except (OSError, MapError):
        # Do not follow a replaced parent even during cleanup. Leave a partial
        # candidate for review if containment can no longer be established.
        try:
            inspect_path(destination, "directory", required=True)
            for path in created:
                metadata = path.lstat()
                if is_link(metadata) or not stat.S_ISREG(metadata.st_mode):
                    raise MapError("output changed during creation")
                path.unlink()
            destination.rmdir()
        except (OSError, MapError):
            pass
        raise
    return destination


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    language = language_from_args(argv)
    parser = LocalizedParser(language, description=tr('map_description', language))
    parser.add_argument('--language', choices=LANGUAGES, default=language, help=tr('language', language))
    parser.add_argument("command", nargs="?", choices=("check", "render"), default="check")
    parser.add_argument("--check", action="store_true", help=tr('map_check', language))
    parser.add_argument("--root", default=".", help=tr('map_root', language))
    parser.add_argument("--manifest", default="project-map.json", help=tr('map_manifest', language))
    parser.add_argument("--require-files", action="store_true", help=tr('map_require', language))
    parser.add_argument("--output-dir", help=tr('map_output', language))
    args = parser.parse_args(argv)
    if args.command == "render" and args.check:
        parser.error("--check cannot be combined with render")
    if args.command == "render" and not args.output_dir:
        parser.error("render requires --output-dir")
    if args.command == "check" and args.output_dir:
        parser.error("--output-dir is valid only for render")
    try:
        root = project_root(args.root)
        data = load_manifest(root, args.manifest)
        nodes, missing = validate_manifest(data, root, args.require_files)
        if args.command == "render":
            route(args.output_dir, "output directory")
            destination = root / args.output_dir
            contents = render_navigation(nodes, root, destination, missing, args.language)
            write_new_outputs(root, args.output_dir, contents)
            print(tr("map_rendered", args.language, files=len(FILES), missing=len(missing)))
        else:
            print(tr("map_valid", args.language, nodes=len(nodes), missing=len(missing)))
        return 0
    except (MapError, OSError, RecursionError) as exc:
        # OS errors may contain source paths; emit only the stable errno.
        detail = "filesystem error (errno {})".format(exc.errno) if isinstance(exc, OSError) else str(exc)
        print("ERROR: " + translate_error(detail, args.language), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
