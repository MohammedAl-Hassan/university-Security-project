import http.server
import socketserver
import json
import base64
import os
import webbrowser
from urllib.parse import urlparse, parse_qs

PORT = 8000

class CryptoBrowserHandler(http.server.SimpleHTTPRequestHandler):
    
    # دالة Vigenere للنصوص
    def vigenere_cipher(self, text, key, decrypt=False):
        text = text.upper().replace(" ", "")
        key = key.upper().replace(" ", "")
        if not text or not key: return "Error"
        extended_key = (key * (len(text) // len(key) + 1))[:len(text)]
        result = []
        for t_char, k_char in zip(text, extended_key):
            t_val = ord(t_char) - ord('A')
            k_val = ord(k_char) - ord('A')
            res_val = (t_val - k_val + 26) % 26 if decrypt else (t_val + k_val) % 26
            result.append(chr(res_val + ord('A')))
        return "".join(result)

    # دالة XOR للنصوص
    def xor_text(self, text, key_char, decrypt=False):
        if not text or not key_char: return "Error"
        key = ord(key_char[0])
        if not decrypt:
            result_bytes = bytes([ord(c) ^ key for c in text])
            return base64.b64encode(result_bytes).decode('utf-8')
        else:
            try:
                data_bytes = base64.b64decode(text.strip())
                return bytes([b ^ key for b in data_bytes]).decode('utf-8')
            except: return "Error"

    # استقبال طلبات الـ POST من المتصفح (للتعامل مع النصوص والميديا)
    def do_POST(self):
        # 1. إذا كان الطلب لمعالجة النصوص
        if self.path == '/api/text':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            is_decrypt = (data.get('action') == 'decrypt')
            if data.get('algo') == 'vigenere':
                res = self.vigenere_cipher(data.get('text'), data.get('key'), is_decrypt)
            else:
                res = self.xor_text(data.get('text'), data.get('key'), is_decrypt)
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"result": res}).encode('utf-8'))
            
        # 2. إذا كان الطلب لمعالجة الميديا والملفات الكبيرة
        elif self.path == '/api/media':
            # قراءة نوع الـ Boundary المستخدم في رفع الملفات عبر المتصفح
            content_type = self.headers['Content-Type']
            content_length = int(self.headers['Content-Length'])
            
            # قراءة البيانات بالكامل بصيغة بايتات نقية من المتصفح
            raw_data = self.rfile.read(content_length)
            
            # استخراج الـ Key الممرر في الهيدر لسهولة الفصل الثنائي
            key_int = int(self.headers.get('X-Crypto-Key', '123')) % 256
            filename = self.headers.get('X-File-Name', 'processed_file.dat')

            # معالجة البايتات بسرعة فائقة جداً ومباشرة
            processed_bytes = bytearray(b ^ key_int for b in raw_data)
            
            # تحديد الاسم الجديد للملف المعالج تلقائياً
            if filename.startswith("Encrypted_"):
                output_name = filename.replace("Encrypted_", "Decrypted_")
            else:
                output_name = "Encrypted_" + filename

            # إرسال الملف مباشرة للمتصفح ليقوم بتحميله في مجلد الـ Downloads فوراً
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{output_name}"')
            self.end_headers()
            self.wfile.write(processed_bytes)

if __name__ == '__main__':
    # إخبار بايتون بتشغيل السيرفر المدمج على الهوست المحلي
    handler = CryptoBrowserHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serever started! Please open your browser and go to: http://localhost:{PORT}")
        # فتح المتصفح تلقائياً فور تشغيل ملف البايثون
        webbrowser.open(f"http://localhost:{PORT}")
        httpd.serve_forever()