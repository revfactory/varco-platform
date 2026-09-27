"""작업자 B 전용 모의 VARCO 서버(포트 18766): TTS·VC·Face·Translate·화자 목록."""
import base64, io, json, wave
from http.server import BaseHTTPRequestHandler, HTTPServer
def wav(sec=1.2):
    b=io.BytesIO(); w=wave.open(b,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100); w.writeframes(b'\x10\x00'*int(44100*sec)); w.close(); return b.getvalue()
VOICES=[{"speaker_uuid":f"u-{n}-{e}","speaker_name":f"{n}({ek})","saas_name":None,"description":d}
  for n,d in [("실라린","남성, 노년, 고음, 거침, 노련한"),("하린","여성, 청년, 저음, 건조, 냉소"),("도윤","남성, 중년, 저음, 거만"),("민서","여성, 청년, 고음, 밝음")]
  for e,ek in [("n","중립"),("a","분노"),("h","행복"),("s","슬픔")]]
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def send(self,code,body):
        body=json.dumps(body,ensure_ascii=False).encode(); self.send_response(code); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.headers.get('OPENAPI_KEY')!='good': return self.send(401,{'message':'Unauthorized'})
        return self.send(200,VOICES)
    def do_POST(self):
        raw=self.rfile.read(int(self.headers.get('Content-Length',0)))
        if self.headers.get('OPENAPI_KEY')!='good': return self.send(401,{'message':'Unauthorized'})
        body=json.loads(raw or b'{}')
        a=base64.b64encode(wav()).decode()
        if self.path.startswith('/tts') or self.path.startswith('/vc'): return self.send(200,{'audio':a,'media_type':'wav'})
        if self.path.startswith('/fa/'): return self.send(200,{'id':body.get('id'),'success':True,'blendshape':{'exportFps':30,'numPoses':2,'numFrames':2,'faceNames':['jawOpen','eyeBlinkLeft'],'weightMat':[[0.1,0],[0.3,0.1]]}})
        if self.path.startswith('/mt/'):
            t=body['source_text']; lang=body['target_lang']
            return self.send(200,dict(body,target_text=f"<{lang}>"+t))
        return self.send(404,{})
HTTPServer(('127.0.0.1',18766),H).serve_forever()
