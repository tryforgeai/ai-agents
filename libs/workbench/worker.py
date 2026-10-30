"""One process per stateless demo; isolated tracing and bounded execution."""
import asyncio
import contextlib
import inspect
import io
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
for library in ('adk_patterns', 'llm_patterns'):
    sys.path.insert(0, str(ROOT/'libs'/library/'src'))


def redact(text):
    for name, value in os.environ.items():
        if len(value) >= 6 and any(word in name.upper() for word in ('KEY','TOKEN','SECRET','PASSWORD')):
            text = text.replace(value, '[REDACTED]')
    return text


if __name__ == '__main__':
    output = io.StringIO()
    try:
        payload = json.load(sys.stdin)
        with contextlib.ExitStack() as stack, contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            import demos
            # Name comes from the server-side catalogue, never a user Python expression.
            from catalog import catalog
            entry = catalog()[payload['id']]
            if entry['demo'] == 'crewai_wrapper':
                os.environ['CREWAI_STORAGE_DIR'] = stack.enter_context(tempfile.TemporaryDirectory())
                os.environ['OTEL_SDK_DISABLED'] = 'true'
            function = getattr(demos, entry['demo'])
            result = function(payload['data'])
            if inspect.isawaitable(result):
                result = asyncio.run(result)
        answer = {'ok':True, 'result':result, 'logs':output.getvalue()[-12000:]}
    except Exception as error:
        answer = {'ok':False, 'error':f'{type(error).__name__}: {error}',
                  'logs':output.getvalue()[-12000:]}
    print(redact(json.dumps(answer, ensure_ascii=False, default=str)))
