# Lokaler Testserver wie Netlify: /seite -> seite.html, /seite.html -> 301 /seite. Aufruf: python3 devserver.py site
import http.server, os, sys
ROOT = sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def do_GET(s):
        pfad = s.path.split("?")[0].split("#")[0]
        if pfad.endswith(".html") and pfad != "/404.html":
            s.send_response(301); s.send_header("Location", "/" if pfad == "/index.html" else pfad[:-5]); s.end_headers(); return
        if pfad != "/" and "." not in os.path.basename(pfad) and os.path.exists(os.path.join(ROOT, pfad.lstrip("/") + ".html")):
            s.path = pfad + ".html"
        return super().do_GET()
http.server.ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
