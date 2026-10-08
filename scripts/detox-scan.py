#!/usr/bin/env python3
"""Bounded, read-only AI instruction scanner (Python 3.8+, stdlib only).

Source text is untrusted data and is never executed or included in findings.
Use --root PROJECT or --files FILE...; home and filesystem-root discovery are
refused. References are checked inside the selected scope, never followed.
Exit codes: 0 clean, 1 findings, 2 usage/output/no-input error, 3 partial scan.
Only an explicitly requested, new --json report file may be written.
"""
import argparse
import bisect
import json
import ntpath
import os
import re
import stat
import sys
from urllib.parse import unquote
from locale_data import LANGUAGES, LocalizedParser, language_from_args, text as tr

ENTRY_NAMES = {
    'CLAUDE.md', 'CLAUDE.local.md', 'AGENTS.md', 'CODEX.md', 'GEMINI.md',
    'QWEN.md', 'SKILL.md', 'core-rules.md',
}
ENTRY_NAMES_LOWER = {name.lower() for name in ENTRY_NAMES}
SCAN_DIRS = {
    '.claude', '.codex', '.agents', '.ai', '.cursor', '.gemini', '.qwen',
    '.grok', 'skills', 'skill', 'prompts', 'instructions', 'rules', 'policies',
    'workflows', 'agents', 'personas', 'context', 'contexts', 'memory',
    'memories', 'knowledge', 'specs', 'specifications',
}
SKIP_DIRS = {
    '.git', 'node_modules', 'vendor', 'dist', 'build', 'coverage',
    '__pycache__', '.venv', 'venv', '.pytest_cache', 'ms-playwright',
    '.cache', 'cache', 'tmp', 'temp', 'backup', 'backups',
    '.ai-detox', '.audit-tmp',
}
SENSITIVE_DIRS = {'.secrets', '.ssh', '.aws', '.gnupg', '.azure'}
SENSITIVE_FILES = {
    '.netrc', '_netrc', '.npmrc', '.pypirc', 'credentials', 'credentials.md',
    'credentials.json', 'credentials.toml', 'credentials.yaml',
    'credentials.yml', 'secrets.json', 'secrets.yaml', 'secrets.yml',
    'id_rsa', 'id_dsa', 'id_ed25519', 'id_ecdsa',
}
MAX_DEPTH = 6
MAX_BYTES = 1024 * 1024
MAX_FILES = 5000
MAX_TOTAL_BYTES = 64 * 1024 * 1024
REPARSE_POINT = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)

SECRET_PATTERNS = {
    'openai_key': r'sk-[A-Za-z0-9_.-]{20,}',
    'cloudflare_key': r'cfk_[A-Za-z0-9]{20,}',
    'google_oauth': r'GOCSPX-[A-Za-z0-9_-]{10,}',
    'github_pat': r'gh[pousr]_[A-Za-z0-9]{20,}',
    'github_fine_grained_pat': r'github_pat_[A-Za-z0-9_]{20,}',
    'private_key': r'-----BEGIN [A-Z ]*PRIVATE KEY(?:-----)?',
    'refresh_token': r'1//0[A-Za-z0-9_-]{30,}',
    'url_userpass': r'://[A-Za-z0-9_.-]+:[^@/\s]{1,}@',
    'aws_key': r'(?:AKIA|ASIA)[0-9A-Z]{16}',
}
# Quoted or unquoted assignments in common shell/JSON/YAML/TOML forms. Values
# stay in memory only long enough to remove them from path metadata as well.
CREDENTIAL_ASSIGNMENT_RX = re.compile(
    r'''(?ix)
    (?<![\w]) ["']?
    (?:[\w-]* (?:api[_-]?key|access[_-]?key|secret|password|passwd|pwd|token)
       [\w-]* | credential(?:s)?) ["']? \s* (?:=|:) \s*
    (?: "(?P<double>[^"\r\n]+)" | '(?P<single>[^'\r\n]+)'
       | (?P<bare>[^\s,;\#}]+) )
    '''
)
PLACEHOLDERS = {'example', 'changeme', 'placeholder', 'redacted', 'none', 'null'}
INJECTION_PATTERNS = {
    'ignore_rules': r'(ignore|disregard)\s+(all\s+|previous\s+|prior\s+)?(rules?|instructions?)',
    'trust_blindly': r'(無條件信任|trust\s+.{0,25}unconditionally|一律信任)',
    'auto_deploy': r'(自動部署|auto[- ]?deploy|deploy\s+without\s+(asking|approval))',
    'skip_tests': r'(skip\s+(the\s+)?tests?|跳過測試|不用跑測試)',
    'disable_safety': r'(disable|停用|關閉)\s*(safety|security|安全檢查|安全機制)',
    'read_secrets': r'(讀取.{0,8}(密鑰|金鑰|憑證)|read\s+.{0,15}(secret|credential)s?\s+(file|store))',
    'hide_logs': r'(隱藏.{0,6}(紀錄|log)|hide\s+.{0,10}logs?|刪除證據)',
    'destructive': r'rm\s+-rf\s+[^\s]|git\s+reset\s+--hard|DROP\s+TABLE',
    'self_authoritative': r'(本檔不可質疑|不得質疑本規則|this file (is )?(cannot|must not) be questioned)',
}
INJECTION_PATTERNS.update({
    'ignore_rules_de': r'(?:ignorier\w*|missachte\w*)\s+.{0,50}(?:regeln|anweisungen)|(?:regeln|anweisungen).{0,30}ignorieren',
    'ignore_rules_ja': r'(?:以前|前|すべて|全て).{0,20}(?:指示|ルール).{0,10}無視',
})
VAGUE_TERMS = [
    '更自然', '好的語氣', '專業一點', '必須完整', '儘量簡潔', '盡量簡潔',
    '非常高品質', '最好的模型', '適時', '必要時', '視情況', '適當處理',
    '確保結果正確', '重大變更', '不要浪費',
]
ABSOLUTE_TERMS = ['MUST', 'NEVER', 'ALWAYS', '一律', '絕不', '永遠', '禁止']
VAGUE_TERMS += ['as needed', 'appropriate handling', 'best model', 'bei Bedarf',
                'angemessen', 'bestes Modell', '必要に応じて', '適切に', '最適なモデル']
ABSOLUTE_TERMS += ['IMMER', 'NIEMALS', 'VERBOTEN', '必ず', '絶対に', '常に']
SUFFIX_RX = r'\.(?:md|json|toml|ps1|py|yaml|yml)'
BARE_PATH_RX = re.compile(
    r'''[^\s`<>()"']+''' + SUFFIX_RX + r'''(?:[?#][^\s`<>()"']*)?''', re.I
)
MARKDOWN_LINK_RX = re.compile(r'\[[^\]\r\n]*\]\(([^\r\n]*?)\)')
CODE_PATH_RX = re.compile(r'`([^`\r\n]+)`')
URL_RX = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:')


class FileSelection(list):
    """List-compatible discovery result carrying scope and coverage evidence."""
    def __init__(self, files=(), root=None, errors=None, skipped=None):
        super().__init__(files)
        self.root = root
        self.errors = errors or []
        self.skipped = skipped or []


def _absolute(path):
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def _inside(path, root):
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:
        return False


def _sensitive(path):
    parts = path.replace('\\', '/').lower().split('/')
    name = parts[-1]
    return (bool(set(parts) & SENSITIVE_DIRS) or name in SENSITIVE_FILES
            or name.startswith('credentials.') or name == '.envrc'
            or name == '.env' or name.startswith('.env.')
            or name.endswith(('.pem', '.key', '.p12', '.pfx')))


def _linked(info):
    # is_symlink alone does not catch Windows junctions or other reparse points.
    return (stat.S_ISLNK(info.st_mode)
            or bool(getattr(info, 'st_file_attributes', 0) & REPARSE_POINT))


def _path_problem(path, root=None):
    """Validate EVERY lexical ancestor before any following stat/open call."""
    if root is not None and not _inside(path, root):
        return 'outside_scope'
    if _sensitive(path):
        return 'sensitive_excluded'
    ancestors = []
    current = path
    while True:
        ancestors.append(current)
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    for ancestor in reversed(ancestors):
        try:
            info = os.lstat(ancestor)
        except FileNotFoundError:
            return 'missing'
        except OSError:
            return 'unreadable'
        if _linked(info):
            return 'linked_excluded'
    return None


def _issue(path, code, operation='read', line=None):
    result = {'file': path, 'code': code, 'operation': operation}
    if line is not None:
        result['line'] = line
    return result


def find_files(root=None, explicit=None, max_depth=MAX_DEPTH):
    """Discover safely; failures are retained in FileSelection.errors."""
    if max_depth < 0:
        raise ValueError('max_depth must be nonnegative')
    if explicit is not None:
        files = sorted({_absolute(path) for path in explicit})
        scope = os.path.commonpath([os.path.dirname(path) for path in files]) if files else None
        selected = FileSelection(root=scope)
        for path in files:
            problem = _path_problem(path)
            if problem:
                selected.errors.append(_issue(path, problem, 'select'))
                continue
            try:
                if not stat.S_ISREG(os.lstat(path).st_mode):
                    selected.errors.append(_issue(path, 'not_file', 'select'))
                    continue
            except OSError:
                selected.errors.append(_issue(path, 'unreadable', 'select'))
                continue
            selected.append(path)
        return selected
    if root is None:
        raise ValueError('an explicit project root or file selection is required')
    root = _absolute(root)
    if root == _absolute(os.path.expanduser('~')) or os.path.dirname(root) == root:
        raise ValueError('home and filesystem-root discovery are refused')
    selected = FileSelection(root=root)
    problem = _path_problem(root)
    if problem:
        selected.errors.append(_issue(root, problem, 'discover'))
        return selected
    if not os.path.isdir(root):
        selected.errors.append(_issue(root, 'not_directory', 'discover'))
        return selected
    pending = [(root, 0)]
    while pending:
        directory, depth = pending.pop()
        # Recheck in case an entry changed after its parent's enumeration.
        problem = _path_problem(directory, root)
        if problem:
            selected.errors.append(_issue(directory, problem, 'discover'))
            continue
        try:
            with os.scandir(directory) as entries:
                children = sorted(entries, key=lambda entry: entry.name)
        except OSError:
            selected.errors.append(_issue(directory, 'unreadable', 'discover'))
            continue
        rel_parts = os.path.relpath(directory, root).replace('\\', '/').lower().split('/')
        in_scan_dir = bool(set(rel_parts) & SCAN_DIRS)
        next_dirs = []
        for entry in children:
            path = _absolute(entry.path)
            if entry.name.lower() in SKIP_DIRS or _sensitive(path):
                selected.skipped.append(_issue(path, 'policy_excluded', 'discover'))
                continue
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError:
                selected.errors.append(_issue(path, 'unreadable', 'discover'))
                continue
            if _linked(info):
                selected.skipped.append(_issue(path, 'linked_excluded', 'discover'))
                continue
            if stat.S_ISDIR(info.st_mode):
                if depth >= max_depth:
                    selected.errors.append(_issue(path, 'depth_limit', 'discover'))
                else:
                    next_dirs.append((path, depth + 1))
            elif stat.S_ISREG(info.st_mode):
                if entry.name.lower() in ENTRY_NAMES_LOWER or (
                        in_scan_dir and entry.name.lower().endswith('.md')):
                    if len(selected) >= MAX_FILES:
                        selected.errors.append(_issue(path, 'file_count_limit', 'discover'))
                        pending = []
                        next_dirs = []
                        break
                    selected.append(path)
        pending.extend(reversed(next_dirs))
    selected.sort()
    return selected


def _read_checked(path, root, max_bytes):
    problem = _path_problem(path, root)
    if problem:
        return None, problem
    try:
        before = os.lstat(path)
        if not stat.S_ISREG(before.st_mode):
            return None, 'not_file'
        if before.st_size > max_bytes:
            return None, 'size_limit'
        flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, 'rb') as source:
            opened = os.fstat(source.fileno())
            if (_linked(opened) or not stat.S_ISREG(opened.st_mode)
                    or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
                    or _path_problem(path, root)):
                return None, 'changed_during_read'
            data = source.read(max_bytes + 1)
            after = os.fstat(source.fileno())
            if (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                return None, 'changed_during_read'
        if len(data) > max_bytes:
            return None, 'size_limit'
        return data, None
    except OSError:
        return None, 'unreadable'


def read(path):
    """Compatibility helper: failed reads now raise, rather than appear empty."""
    data, problem = _read_checked(_absolute(path), None, MAX_BYTES)
    if problem:
        raise OSError(problem)
    return data.decode('utf-8', errors='strict')


def _reference_value(value, markdown=False):
    value = value.strip()
    if markdown:
        if value.startswith('<') and '>' in value:
            value = value[1:value.index('>')]
        else:
            # An optional Markdown title is not part of the destination.
            value = re.sub(r'''\s+["'][^"']*["']\s*$''', '', value)
    value = value.strip().rstrip('.,;')
    if not value or value.startswith('#'):
        return None
    if value.startswith('//') or (URL_RX.match(value) and not re.match(r'^[A-Za-z]:[\\/]', value)):
        return None
    value = unquote(value.split('#', 1)[0].split('?', 1)[0])
    if not re.search(SUFFIX_RX + r'$', value, re.I):
        return None
    return value


def _references(text):
    """Yield (line, local destination); URLs/anchors are ignored as units."""
    for line_number, line in enumerate(text.splitlines(), 1):
        occupied = []
        values = []
        for pattern, markdown in ((MARKDOWN_LINK_RX, True), (CODE_PATH_RX, False)):
            for match in pattern.finditer(line):
                if any(start <= match.start() < end for start, end in occupied):
                    continue
                occupied.append(match.span())
                value = _reference_value(match.group(1), markdown)
                if value:
                    values.append((match.start(), value))
        for match in BARE_PATH_RX.finditer(line):
            if any(start <= match.start() < end for start, end in occupied):
                continue
            value = _reference_value(match.group())
            if value:
                values.append((match.start(), value))
        seen = set()
        for _, value in sorted(values):
            if value not in seen:
                seen.add(value)
                yield line_number, value


def _resolve_reference(source, value, root):
    # Windows absolute references on POSIX must not turn into relative paths.
    if os.name != 'nt' and ntpath.isabs(value) and not value.startswith('/'):
        return None, 'outside_scope'
    candidate = value.replace('\\', os.sep).replace('/', os.sep)
    target = _absolute(candidate if os.path.isabs(candidate)
                       else os.path.join(os.path.dirname(source), candidate))
    problem = _path_problem(target, root)
    if problem:
        return None, problem
    try:
        if not stat.S_ISREG(os.lstat(target).st_mode):
            return None, 'not_file'
    except OSError:
        return None, 'unreadable'
    return target, None


def _cycles(graph):
    """Iterative SCC detection: one representative directed cycle per SCC."""
    seen = set()
    finish = []
    for start in sorted(graph):
        if start in seen:
            continue
        seen.add(start)
        stack = [(start, iter(sorted(graph[start])))]
        while stack:
            node, edges = stack[-1]
            other = next(edges, None)
            if other is None:
                finish.append(node)
                stack.pop()
            elif other not in seen:
                seen.add(other)
                stack.append((other, iter(sorted(graph[other]))))
    reverse = {node: [] for node in graph}
    for node, edges in graph.items():
        for other in edges:
            reverse[other].append(node)
    assigned = set()
    result = []
    for start in reversed(finish):
        if start in assigned:
            continue
        members = []
        pending = [start]
        assigned.add(start)
        while pending:
            node = pending.pop()
            members.append(node)
            for other in sorted(reverse[node], reverse=True):
                if other not in assigned:
                    assigned.add(other)
                    pending.append(other)
        members.sort()
        allowed = set(members)
        if len(members) == 1 and start not in graph[start]:
            continue
        active = {}
        visited = set()
        representative = []
        stack = [(members[0], iter(sorted(graph[members[0]] & allowed)))]
        active[members[0]] = 0
        visited.add(members[0])
        while stack and not representative:
            node, edges = stack[-1]
            other = next(edges, None)
            if other is None:
                active.pop(node)
                stack.pop()
            elif other in active:
                representative = [frame[0] for frame in stack[active[other]:]] + [other]
            elif other not in visited:
                active[other] = len(stack)
                visited.add(other)
                stack.append((other, iter(sorted(graph[other] & allowed))))
        result.append({'files': members, 'cycle': representative})
    return sorted(result, key=lambda item: item['files'])


def _redact_metadata(value, secret_values=()):
    """Never serialize content, including credential-bearing path metadata."""
    if isinstance(value, str):
        for secret in sorted(secret_values, key=lambda item: (-len(item), item)):
            value = value.replace(secret, '[REDACTED]')
        for pattern in SECRET_PATTERNS.values():
            value = re.sub(pattern, '[REDACTED]', value)
        value = CREDENTIAL_ASSIGNMENT_RX.sub('credential=[REDACTED]', value)
        value = ''.join(char if char.isprintable() else '?' for char in value)
        return value
    if isinstance(value, dict):
        return {key: _redact_metadata(item, secret_values) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_metadata(item, secret_values) for item in value]
    return value


def scan(files, root=None, max_bytes=MAX_BYTES):
    """Scan selected files without modifying sources or loading references."""
    if max_bytes <= 0:
        raise ValueError('max_bytes must be positive')
    paths = sorted({_absolute(path) for path in files})
    scope = _absolute(root) if root is not None else getattr(files, 'root', None)
    if scope is None and paths:
        scope = os.path.commonpath([os.path.dirname(path) for path in paths])
    report = {
        'schema_version': 2, 'files_selected': len(paths), 'files_scanned': 0,
        'complete': True, 'errors': list(getattr(files, 'errors', [])),
        'skipped': list(getattr(files, 'skipped', [])),
        'limits': {'max_depth': MAX_DEPTH, 'max_file_bytes': max_bytes,
                   'max_files': MAX_FILES, 'max_total_bytes': MAX_TOTAL_BYTES},
        'dangling_refs': [], 'boundary_refs': [], 'circular_refs': [],
        'secrets': [], 'injections': [], 'vague_rules': [],
        'absolute_terms': [], 'duplicate_blocks': [], 'file_stats': [],
    }
    texts = {}
    refs = {}
    secret_values = set()
    total_bytes = 0
    for index, path in enumerate(paths):
        if index >= MAX_FILES:
            report['errors'].append(_issue(path, 'file_count_limit'))
            break
        if total_bytes >= MAX_TOTAL_BYTES:
            report['errors'].append(_issue(path, 'total_size_limit'))
            break
        data, problem = _read_checked(path, scope, min(max_bytes, MAX_TOTAL_BYTES - total_bytes))
        if problem:
            report['errors'].append(_issue(path, problem))
            continue
        total_bytes += len(data)
        try:
            text = data.decode('utf-8-sig', errors='strict')
        except UnicodeDecodeError:
            report['errors'].append(_issue(path, 'invalid_utf8'))
            continue
        texts[path] = text
        lines = text.splitlines()
        newlines = [position for position, char in enumerate(text) if char == '\n']
        report['file_stats'].append({'path': path, 'lines': len(lines),
                                     'bytes': len(data), 'approx_tokens': len(text) // 3})
        for name, pattern in SECRET_PATTERNS.items():
            for match in re.finditer(pattern, text):
                secret_values.add(match.group())
                if name == 'url_userpass':
                    secret_values.add(match.group().split(':', 2)[-1][:-1])
                report['secrets'].append({'file': path, 'type': name,
                                          'line': bisect.bisect_left(newlines, match.start()) + 1})
        for match in CREDENTIAL_ASSIGNMENT_RX.finditer(text):
            value = next(value for value in match.groupdict().values() if value is not None)
            if value.lower() in PLACEHOLDERS or value.startswith(('$', '${', '<')):
                continue
            secret_values.add(value)
            report['secrets'].append({'file': path, 'type': 'credential_assignment',
                                      'line': bisect.bisect_left(newlines, match.start()) + 1})
        for name, pattern in INJECTION_PATTERNS.items():
            for match in re.finditer(pattern, text, re.I):
                report['injections'].append({'file': path, 'type': name,
                                             'line': bisect.bisect_left(newlines, match.start()) + 1})
        for line_number, line in enumerate(lines, 1):
            for key, terms in (('vague_rules', VAGUE_TERMS), ('absolute_terms', ABSOLUTE_TERMS)):
                for term in terms:
                    if term in line:
                        report[key].append({'file': path, 'line': line_number, 'term': term})
                        break
        targets = set()
        for line_number, destination in _references(text):
            target, problem = _resolve_reference(path, destination, scope)
            if problem:
                finding = {'file': path, 'line': line_number, 'reason': problem}
                if problem in ('missing', 'not_file'):
                    report['dangling_refs'].append(finding)
                elif problem == 'unreadable':
                    report['errors'].append(_issue(path, problem, 'reference_stat', line_number))
                else:
                    report['boundary_refs'].append(finding)
            else:
                targets.add(target)
        refs[path] = targets
    report['files_scanned'] = len(texts)
    graph = {path: targets & set(texts) for path, targets in refs.items()}
    report['circular_refs'] = _cycles(graph)
    blocks = {}
    for path, text in texts.items():
        newline_positions = [position for position, char in enumerate(text) if char == '\n']
        for match in re.finditer(r'(?:\A|\n\s*\n)(.*?)(?=\n\s*\n|\Z)', text, re.S):
            paragraph = match.group(1)
            normalized = ' '.join(paragraph.split())
            if len(normalized) >= 80 and paragraph.count('\n') >= 2:
                line = bisect.bisect_left(newline_positions, match.start(1)) + 1
                # Full normalized block is the identity; no excerpts or hashes.
                blocks.setdefault(normalized, []).append({'file': path, 'line': line})
    for normalized, locations in sorted(blocks.items()):
        if len({location['file'] for location in locations}) > 1:
            report['duplicate_blocks'].append({'block_id': len(report['duplicate_blocks']) + 1,
                                               'characters': len(normalized), 'locations': locations})
    report['complete'] = not report['errors']
    for key in ('errors', 'skipped', 'dangling_refs', 'boundary_refs', 'secrets',
                'injections', 'vague_rules', 'absolute_terms'):
        report[key].sort(key=lambda item: (item['file'], item.get('line', 0),
                                          item.get('type', item.get('code', item.get('reason', '')))))
    return _redact_metadata(report, secret_values)


def print_report(report, language='zh-TW'):
    print(tr('scan_title', language))
    status = tr('scan_complete' if report['complete'] else 'scan_partial', language)
    print(tr('scan_counts', language, scanned=report['files_scanned'], selected=report['files_selected'], status=status))
    print(tr('scan_totals', language, lines=sum(item['lines'] for item in report['file_stats']),
             tokens=format(sum(item['approx_tokens'] for item in report['file_stats']), ',')))
    for key in ('errors', 'secrets', 'injections', 'dangling_refs', 'boundary_refs',
                'circular_refs', 'duplicate_blocks', 'vague_rules', 'absolute_terms'):
        print('\n%s: %d' % (tr(key, language), len(report[key])))
        for item in report[key][:20]:
            if key == 'circular_refs':
                print('  ' + ' -> '.join(item['cycle']))
            elif key == 'duplicate_blocks':
                locations = ', '.join('%s:%d' % (loc['file'], loc['line']) for loc in item['locations'])
                print('  ' + tr('block', language, id=item['block_id'], characters=item['characters'], locations=locations))
            else:
                print('  %s%s [%s]' % (item['file'],
                      ':' + str(item['line']) if 'line' in item else '',
                      item.get('type', item.get('code', item.get('reason', item.get('term', ''))))))
        if len(report[key]) > 20:
            print('  ... ' + tr('more', language, count=len(report[key]) - 20))
    print('\n' + tr('excluded', language, count=len(report['skipped'])))
    print(tr('heuristic', language))
    print(tr('limitations', language))


def _write_report(path, report, inputs):
    target = _absolute(path)
    parent = os.path.dirname(target)
    if _sensitive(target):
        raise ValueError('report destination must not be a sensitive file')
    if target in {_absolute(source) for source in inputs}:
        raise ValueError('report path must not be an input file')
    if _path_problem(parent):
        raise ValueError('report parent must exist and must not be linked or sensitive')
    if not os.path.isdir(parent) or os.path.lexists(target):
        raise ValueError('report requires a new file in an existing directory')
    # Exclusive creation prevents overwriting an existing source/link/report.
    with open(target, 'x', encoding='utf-8', newline='\n') as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write('\n')


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass
    language = language_from_args(argv)
    parser = LocalizedParser(language, description=tr('scan_description', language))
    parser.add_argument('--language', choices=LANGUAGES, default=language, help=tr('language', language))
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--root', help=tr('scan_root', language))
    selection.add_argument('--files', nargs='+', help=tr('scan_files', language))
    parser.add_argument('--json', help=tr('scan_json', language))
    parser.add_argument('--max-depth', type=int, default=MAX_DEPTH, help=tr('scan_depth', language))
    parser.add_argument('--max-bytes', type=int, default=MAX_BYTES, help=tr('scan_bytes', language))
    args = parser.parse_args(argv)
    if args.max_depth < 0 or args.max_bytes <= 0:
        parser.error(tr('scan_limits_error', language))
    try:
        files = find_files(args.root, args.files, args.max_depth)
        report = scan(files, max_bytes=args.max_bytes)
        report['limits']['max_depth'] = args.max_depth
        if args.json:
            _write_report(args.json, report, files)
    except (ValueError, OSError):
        print(tr('scan_invalid', language), file=sys.stderr)
        return 2
    print_report(report, args.language)
    if not report['complete']:
        return 3
    if not report['files_scanned']:
        print(tr('scan_empty', language), file=sys.stderr)
        return 2
    risk_keys = ('secrets', 'injections', 'dangling_refs', 'boundary_refs',
                 'circular_refs', 'duplicate_blocks')
    return 1 if any(report[key] for key in risk_keys) else 0


if __name__ == '__main__':
    sys.exit(main())
