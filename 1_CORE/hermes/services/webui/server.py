import os, argparse
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.request, json

API = f"http://{os.getenv('HERMES_API_HOST','localhost')}:{os.getenv('HERMES_API_PORT','8788')}"

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path in ("/chat","/ingest"):
            length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(length)
            req = urllib.request.Request(API+self.path, data=body, method='POST', headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req) as r:
                data = r.read()
                self.send_response(200)
                self.send_header('Content-Type','application/json')
                self.end_headers()
                self.wfile.write(data)
        else:
            self.send_error(404)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default=os.getenv('HERMES_WEB_HOST','localhost'))
    parser.add_argument('--port', type=int, default=int(os.getenv('HERMES_WEB_PORT','8787')))
    args = parser.parse_args()
    os.chdir(os.path.dirname(__file__))
    HTTPServer((args.host,args.port), Handler).serve_forever()
