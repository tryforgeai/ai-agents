"""Usage: python vision_call.py path/to/image.png (uses a vision-capable model)."""
import sys
from llm_patterns import CompletionClient, vision_messages

if __name__ == "__main__":
    client = CompletionClient.from_env()
    try:
        print(client.complete(messages=vision_messages(
            "先转录图片中的文字和公式，标记不清楚的部分，再简要解释。", sys.argv[1:])))
    finally:
        client.close()
