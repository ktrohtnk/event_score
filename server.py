import os
import json
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

API_KEY = os.environ.get("GEMINI_API_KEY")

class FluxusHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
            return super().do_GET()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == '/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            noun = data.get('noun', 'it')
            
            if not API_KEY:
                # Fallback if no API key
                response = {
                    "text": f"(API_KEY is not set!)\n\nPlease set GEMINI_API_KEY environment variable.\n\nFallback instruction:\nHide the {noun}."
                }
            else:
                # Call Gemini API
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
                
                prompt = f"""You are a Fluxus artist like George Brecht or Yoko Ono. 
Write a very short, minimalist, absurd, or poetic instructional 'event score' based on the word '{noun}'.
It must be 1 to 3 short sentences. 
Do not include any title, intro, or explanation. 
Output ONLY the instruction text."""

                req_body = json.dumps({
                    "contents": [{"parts":[{"text": prompt}]}]
                }).encode('utf-8')

                req = urllib.request.Request(url, data=req_body, headers={'Content-Type': 'application/json'})
                
                try:
                    with urllib.request.urlopen(req) as f:
                        res_data = json.loads(f.read().decode('utf-8'))
                        text = res_data['candidates'][0]['content']['parts'][0]['text']
                        response = {"text": text.strip()}
                except Exception as e:
                    response = {"text": f"Error calling API: {str(e)}"}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

if __name__ == '__main__':
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, FluxusHandler)
    print(f"Starting Fluxus AI server on http://localhost:{port}")
    if not API_KEY:
        print("WARNING: GEMINI_API_KEY environment variable is not set. The server will run in fallback mode.")
    httpd.serve_forever()
