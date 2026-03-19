import sys
from urllib.parse import quote_plus
import os

def parse_args():
    args = sys.argv[1:]
    result = {
        "url": None,
        "size": None,
        "devtools": None
    }

    for arg in args:
        if arg.startswith("-size="):
            try:
                w, h = arg[6:].split("x")
                result["size"] = (int(w), int(h))
            except:
                print("Geçersiz boyut formatı. Örnek: -size=800x600")

        elif arg.startswith("-devtools="):
            val = arg[10:].lower()
            result["devtools"] = (val == "on")

        else:
            result["url"] = arg

    return result


def resolve_url(url, BASE_DIR):
    url = url.strip()
    if not url:
        return None

    if url.lower().endswith(".pdf"):
        viewer_path = f"file://{BASE_DIR}/pdfjs/web/viewer.html"
        if not url.startswith(("http", "file")):
            url = f"file://{os.path.abspath(url)}"
        return f"{viewer_path}?file={url}"

    if url.startswith(("http://", "https://", "file:///")):
        pass
    elif url.startswith("/"):
        url = "file://" + url
    elif "." not in url or " " in url:
        url = f"https://www.google.com/search?q={quote_plus(url)}"
    else:
        url = "https://" + url

    return url
    