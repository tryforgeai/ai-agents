"""Week 02: local image → data URL → OpenAI-compatible content parts."""
import base64
from pathlib import Path


def image_data_url(path, *, max_bytes=20_000_000):
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    with Path(path).open("rb") as stream:
        data = stream.read(max_bytes + 1)
    if not data or len(data) > max_bytes:
        raise ValueError("image is empty or exceeds max_bytes")
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        mime = "image/png"
    elif data.startswith(b'\xff\xd8\xff'):
        mime = "image/jpeg"
    elif data[:6] in (b'GIF87a', b'GIF89a'):
        mime = "image/gif"
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        mime = "image/webp"
    else:
        raise ValueError("supported image signatures: PNG, JPEG, GIF, WebP")
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def vision_messages(question, paths):
    return [{"role": "user", "content": [
        {"type": "text", "text": question},
        *[{"type": "image_url", "image_url": {"url": image_data_url(path)}} for path in paths],
    ]}]
