import json
import urllib.error
import urllib.request

from app.core.config import settings


def main() -> None:
    if not settings.groq_api_key:
        print("No GROQ_API_KEY found. Check backend\\.env and config.py.")
        return
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/models",
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "User-Agent": "InterviewOS/0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            models = json.loads(response.read())["data"]
            ids = [m["id"] for m in models]
            print(f"Key works. {len(ids)} models visible.")
            print("Configured model available:", settings.groq_model in ids)
    except urllib.error.HTTPError as error:
        print(f"Request failed with HTTP {error.code}. Check the key and account.")


if __name__ == "__main__":
    main()