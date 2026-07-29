"""Static server for the site. A plain `python3 -m http.server` fails here because argparse
evaluates os.getcwd() as a default before parsing, and the launcher's cwd is unreadable."""
import http.server, os, socketserver
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site"))
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", 8899), http.server.SimpleHTTPRequestHandler) as d:
    print("serving site on 8899")
    d.serve_forever()
