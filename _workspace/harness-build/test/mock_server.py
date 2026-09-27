"""varco_client.py 실제 호출 경로 검증용 모의 서버(로컬 전용)."""
import base64, json, io, wave
from http.server import BaseHTTPRequestHandler, HTTPServer
def wav_bytes():
    b=io.BytesIO(); w=wave.open(b,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes(b'\x01\x00'*44100); w.close(); return b.getvalue()
PNG=bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360000000000200015e2c2d3d0000000049454e44ae426082')
POLLS={'n':0}
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def send(self,code,body,ctype='application/json'):
        if isinstance(body,(dict,list)): body=json.dumps(body).encode()
        self.send_response(code); self.send_header('Content-Type',ctype); self.send_header('x-request-id','req-123'); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0)); raw=self.rfile.read(n)
        if self.headers.get('OPENAPI_KEY')!='good': return self.send(401,{'message':'Unauthorized'})
        a=base64.b64encode(wav_bytes()).decode()
        if self.path.endswith('text2sound'): return self.send(200,[{'audio':a},{'audio':a}])
        if self.path.endswith('looping'):
            import time; time.sleep(1.5); return self.send(200,{'audio':a})
        if self.path.endswith('enhance'): return self.send(422,{'detail':'source invalid'})
        if self.path.startswith('/fashion'): return self.send(200,PNG,'image/png')
        if self.path.startswith('/3d'): return self.send(202,{'requestId':'r1','message':'accepted'})
        return self.send(404,{})
    def do_GET(self):
        if self.path.startswith('/inference/result'):
            POLLS['n']+=1
            if POLLS['n']<2: return self.send(202,{'status':'processing'})
            return self.send(200,{'status':'succeeded','model_url':f'http://127.0.0.1:{self.server.server_port}/model.glb'})
        if self.path=='/model.glb': return self.send(200,b'glTF\x02\x00\x00\x00'+b'\x00'*16,'model/gltf-binary')
        return self.send(200,[{'speaker_uuid':'u1','speaker_name':'A'}])
HTTPServer(('127.0.0.1',18765),H).serve_forever()
