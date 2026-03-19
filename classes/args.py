import sys
from urllib.parse import quote_plus
import os

def parse_args():
    args = sys.argv[1:] #argümanlar
    result = {          #argümanlar
        "url": None,
        "size": None,
        "devtools": None
    }

    for arg in args:
        if arg.startswith("-size="): #parametre -size ise
            try:
                w, h = arg[6:].split("x")
                result["size"] = (int(w), int(h)) #iki değeri GENISLIKxYUKSEKLIK olacak biçimde ayır
            except:
                print("Geçersiz boyut formatı. Örnek: -size=800x600")

        elif arg.startswith("-devtools="): #parametre -devtools ise
            val = arg[10:].lower() #argümana verilen değeri (on/off) küçük harfli yap
            result["devtools"] = (val == "on") #değere göre (on/off) devtools'u True

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
    