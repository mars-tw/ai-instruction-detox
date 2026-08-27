#!/usr/bin/env python3
"""
detox-scan.py — AI 指令排毒：唯讀掃描器

掃描 AI 指令檔並回報：懸空引用、循環引用、重複規則、可疑注入、秘密外洩、
自動載入面積。純唯讀，不修改任何檔案。

用法：
    python detox-scan.py --root <專案或家目錄> [--json out.json]
    python detox-scan.py --files a.md b.md [--json out.json]

MIT License
"""
import argparse
import json
import os
import re
import sys

# Windows 終端常見 cp950／big5，強制 UTF-8 輸出避免中文與符號崩潰
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# ── 預設要找的 AI 指令檔 ──────────────────────────────────────────
ENTRY_NAMES = {
    'CLAUDE.md', 'CLAUDE.local.md', 'AGENTS.md', 'CODEX.md',
    'GEMINI.md', 'QWEN.md', 'SKILL.md', 'core-rules.md',
}
SCAN_DIRS = {
    '.claude', '.codex', '.agents', '.ai', '.cursor', '.gemini', '.qwen', '.grok',
    'skills', 'skill', 'prompts', 'instructions', 'rules', 'policies',
    'workflows', 'agents', 'personas', 'context', 'contexts',
    'memory', 'memories', 'knowledge', 'specs', 'specifications',
}
SKIP_DIRS = {
    '.git', 'node_modules', 'vendor', 'dist', 'build', 'coverage',
    '__pycache__', '.venv', 'venv', '.pytest_cache', 'ms-playwright',
}

# ── 偵測樣式 ────────────────────────────────────────────────────
SECRET_PATTERNS = {
    'openai_key': r'sk-[A-Za-z0-9_.-]{20,}',
    'cloudflare_key': r'cfk_[A-Za-z0-9]{20,}',
    'google_oauth': r'GOCSPX-[A-Za-z0-9_-]{10,}',
    'github_pat': r'gh[pousr]_[A-Za-z0-9]{20,}',
    'private_key': r'-----BEGIN [A-Z ]*PRIVATE KEY',
    'refresh_token': r'1//0[A-Za-z0-9_-]{30,}',
    'url_userpass': r'://[A-Za-z0-9_.-]+:[^@/\s]{6,}@',
    'aws_key': r'AKIA[0-9A-Z]{16}',
}

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

VAGUE_TERMS = [
    '更自然', '好的語氣', '專業一點', '必須完整', '儘量簡潔', '盡量簡潔',
    '非常高品質', '最好的模型', '適時', '必要時', '視情況', '適當處理',
    '確保結果正確', '重大變更', '不要浪費',
]

ABSOLUTE_TERMS = ['MUST', 'NEVER', 'ALWAYS', '一律', '絕不', '永遠', '禁止']

PATH_RX = re.compile(
    r'`?((?:[A-Za-z]:[\\/][^`\s()<>"\']+)|(?:\.{1,2}/[^\s`()<>"\']+\.(?:md|json|toml|ps1|py|yaml|yml)))`?'
)


def find_files(root, explicit=None):
    """收集要掃的檔案"""
    if explicit:
        return [os.path.abspath(f) for f in explicit if os.path.isfile(f)]
    found = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        depth = dirpath[len(root):].count(os.sep)
        if depth > 6:
            dirnames[:] = []
            continue
        rel_parts = set(dirpath[len(root):].split(os.sep))
        in_scan_dir = bool(rel_parts & SCAN_DIRS)
        for fn in filenames:
            if fn in ENTRY_NAMES or (in_scan_dir and fn.endswith('.md')):
                found.append(os.path.join(dirpath, fn))
    return found


def read(p):
    try:
        with open(p, encoding='utf-8', errors='replace') as fh:
            return fh.read()
    except Exception:
        return ''


def scan(files):
    report = {
        'files_scanned': len(files),
        'dangling_refs': [],
        'circular_refs': [],
        'secrets': [],
        'injections': [],
        'vague_rules': [],
        'absolute_terms': [],
        'duplicate_blocks': [],
        'file_stats': [],
    }
    texts = {}
    refs = {}

    for p in files:
        t = read(p)
        texts[p] = t
        lines = t.splitlines()
        report['file_stats'].append({
            'path': p,
            'lines': len(lines),
            'bytes': len(t.encode('utf-8')),
            'approx_tokens': len(t) // 3,
        })

        # 懸空引用
        found_refs = set()
        for m in PATH_RX.findall(t):
            cand = m.replace('\\', os.sep).replace('/', os.sep)
            if cand.startswith('.'):
                full = os.path.normpath(os.path.join(os.path.dirname(p), cand))
            else:
                full = cand
            found_refs.add(full)
            if not os.path.exists(full):
                report['dangling_refs'].append({'file': p, 'ref': m})
        refs[p] = found_refs

        # 秘密
        for name, rx in SECRET_PATTERNS.items():
            for mm in re.finditer(rx, t):
                ln = t[:mm.start()].count('\n') + 1
                report['secrets'].append({'file': p, 'type': name, 'line': ln})

        # 注入
        for name, rx in INJECTION_PATTERNS.items():
            for mm in re.finditer(rx, t, re.I):
                ln = t[:mm.start()].count('\n') + 1
                snippet = t[mm.start():mm.start() + 70].replace('\n', ' ')
                report['injections'].append(
                    {'file': p, 'type': name, 'line': ln, 'snippet': snippet})

        # 模糊
        for i, line in enumerate(lines, 1):
            for term in VAGUE_TERMS:
                if term in line:
                    report['vague_rules'].append(
                        {'file': p, 'line': i, 'term': term, 'text': line.strip()[:100]})
                    break

        # 絕對詞
        for i, line in enumerate(lines, 1):
            for term in ABSOLUTE_TERMS:
                if term in line:
                    report['absolute_terms'].append(
                        {'file': p, 'line': i, 'term': term, 'text': line.strip()[:100]})
                    break

    # 循環引用
    for a, ra in refs.items():
        for b in ra:
            if b in refs and a in refs.get(b, set()) and a != b:
                pair = tuple(sorted([a, b]))
                if not any(set(c['pair']) == set(pair) for c in report['circular_refs']):
                    report['circular_refs'].append({'pair': list(pair)})

    # 重複區塊（>=3 行、>=80 字元的段落出現在多檔）
    blocks = {}
    for p, t in texts.items():
        for para in re.split(r'\n\s*\n', t):
            s = ' '.join(para.split())
            if len(s) >= 80 and para.count('\n') >= 2:
                blocks.setdefault(s[:200], set()).add(p)
    for key, ps in blocks.items():
        if len(ps) > 1:
            report['duplicate_blocks'].append({'snippet': key[:120], 'files': sorted(ps)})

    return report


def print_report(r):
    def hdr(t):
        print('\n' + '=' * 62)
        print(t)
        print('=' * 62)

    hdr('AI 指令排毒掃描結果')
    print('掃描檔案數: %d' % r['files_scanned'])
    total_lines = sum(f['lines'] for f in r['file_stats'])
    total_tokens = sum(f['approx_tokens'] for f in r['file_stats'])
    print('總行數: %d ｜ 約略 Token: %s' % (total_lines, format(total_tokens, ',')))

    print('\n-- 最大的 8 個檔（自動載入面積）--')
    for f in sorted(r['file_stats'], key=lambda x: -x['bytes'])[:8]:
        print('  %6d 行  %9s bytes  %s' % (f['lines'], format(f['bytes'], ','), f['path']))

    sections = [
        ('secrets', '秘密外洩（只列位置，不列值）', lambda x: '  %s:%s  [%s]' % (x['file'], x['line'], x['type'])),
        ('injections', '可疑注入／危險指令', lambda x: '  %s:%s  [%s] %s' % (x['file'], x['line'], x['type'], x['snippet'])),
        ('dangling_refs', '懸空引用', lambda x: '  %s -> %s' % (x['file'], x['ref'])),
        ('circular_refs', '循環引用', lambda x: '  %s <-> %s' % (x['pair'][0], x['pair'][1])),
        ('duplicate_blocks', '重複區塊（跨檔）', lambda x: '  %s\n     出現於: %s' % (x['snippet'][:80], ', '.join(x['files']))),
    ]
    for key, title, fmt in sections:
        items = r[key]
        hdr('%s: %d' % (title, len(items)))
        for x in items[:20]:
            print(fmt(x))
        if len(items) > 20:
            print('  ... 另有 %d 筆' % (len(items) - 20))

    hdr('模糊規則: %d ｜ 絕對詞: %d' % (len(r['vague_rules']), len(r['absolute_terms'])))
    for x in r['vague_rules'][:10]:
        print('  [模糊] %s:%s 「%s」 %s' % (x['file'], x['line'], x['term'], x['text'][:60]))
    print('  (絕對詞需人工判斷是否真的不可違反，詳見 --json 輸出)')

    hdr('風險摘要')
    risk = []
    if r['secrets']:
        risk.append('[CRITICAL] %d 處明文秘密' % len(r['secrets']))
    if r['injections']:
        risk.append('[HIGH]     %d 處可疑注入' % len(r['injections']))
    if r['circular_refs']:
        risk.append('[HIGH]     %d 組循環引用' % len(r['circular_refs']))
    if r['dangling_refs']:
        risk.append('[MEDIUM]   %d 處懸空引用' % len(r['dangling_refs']))
    if r['duplicate_blocks']:
        risk.append('[MEDIUM]   %d 處跨檔重複' % len(r['duplicate_blocks']))
    print('  ' + ('\n  '.join(risk) if risk else '[OK]       未發現上述問題'))
    print('\n注意：本工具只做樣式偵測，無法判斷規則的商業價值與衝突語意。')
    print('完整排毒仍需依 SKILL.md 的十二項檢查逐條人工／AI 判讀。')


def main():
    ap = argparse.ArgumentParser(description='AI 指令排毒唯讀掃描器')
    ap.add_argument('--root', help='掃描根目錄')
    ap.add_argument('--files', nargs='+', help='指定檔案')
    ap.add_argument('--json', help='輸出 JSON 路徑')
    a = ap.parse_args()
    if not a.root and not a.files:
        ap.error('需要 --root 或 --files')

    files = find_files(a.root or '.', a.files)
    if not files:
        print('未找到 AI 指令檔')
        return 1
    r = scan(files)
    print_report(r)
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as fh:
            json.dump(r, fh, ensure_ascii=False, indent=2)
        print('\nJSON 已寫出: %s' % a.json)
    return 0


if __name__ == '__main__':
    sys.exit(main())
