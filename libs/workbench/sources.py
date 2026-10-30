"""Read-only course/library source index. Never imports or runs indexed files."""
import json
import os
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
EXTENSIONS = {'.py', '.md', '.ipynb', '.toml', '.sh'}
MAX_BYTES = 2_000_000
EXCLUDE = {'node_modules', '__pycache__', 'site-packages', 'dist', 'build', 'results', 'uploads'}


def allowed(path):
    resolved = path.resolve()
    return (not path.is_symlink() and resolved.is_relative_to(WORKSPACE)
            and not any(part.startswith('.') or part in EXCLUDE
                        for part in path.relative_to(WORKSPACE).parts)
            and path.suffix in EXTENSIONS)


def source_text(path):
    if not allowed(path) or path.stat().st_size > MAX_BYTES:
        raise ValueError('文件不在源码查看范围内或超过 2 MB')
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.ipynb':
        notebook = json.loads(text)
        return '\n\n'.join(f'# Cell {i + 1} [{cell.get("cell_type", "unknown")}]\n' +
                            ''.join(cell.get('source', []))
                            for i, cell in enumerate(notebook.get('cells', [])))
    return text


def scan_sources():
    records = {}
    for root in (WORKSPACE / 'course', WORKSPACE / 'libs'):
        for folder, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d not in EXCLUDE
                             and not (Path(folder) / d).is_symlink())
            for filename in sorted(files):
                path = Path(folder) / filename
                if not allowed(path):
                    continue
                try:
                    content = source_text(path)
                except (ValueError, OSError, UnicodeError):
                    continue
                rel = path.relative_to(WORKSPACE).as_posix()
                records[rel] = {'path': rel, 'name': path.name,
                    'kind': path.suffix.removeprefix('.'),
                    'group': path.relative_to(WORKSPACE).parts[1] if len(path.relative_to(WORKSPACE).parts)>2 else path.relative_to(WORKSPACE).parts[0]+'（索引）', 'content': content}
    return records


def search(records, query='', group='', offset=0, limit=60):
    query = query.casefold().strip()
    matches = []
    for record in records.values():
        if group and record['group'] != group:
            continue
        content = record['content']
        position = content.casefold().find(query) if query else 0
        if query and query not in record['path'].casefold() and position < 0:
            continue
        line = content[:max(position, 0)].count('\n') + 1
        lines = content.splitlines()
        snippet = '\n'.join(lines[max(0, line-2):line+2])[:350]
        matches.append({k: v for k, v in record.items() if k != 'content'} |
                       {'line': line, 'snippet': snippet})
    return {'total':len(matches), 'items':matches[offset:offset+limit]}
