#!/usr/bin/env python3
import socket
import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from secure_comm_lib import SecureCommLib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../udp")))
from udp_client import CertificateClient

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 50000
KEYS_DIR = "client_keys"

class SecureTcpClient:
    def __init__(self, user_id, is_hacker=False):
        self.user_id = user_id
        self.is_hacker = is_hacker # 标记是否为黑客
        self.lib = SecureCommLib()
        self.cert_client = CertificateClient(user_id)
        
        # 准备证书
        self.cert_path = os.path.join(KEYS_DIR, f"{user_id}_cert.sig")
        
        if self.is_hacker:
            print(f"😈 [Hacker] 我是黑客 {user_id}，正在伪造证书...")
            # 黑客没有经过 CA，只是随便写了个假签名，或者用自己的私钥签（CA不认）
            with open(self.cert_path, "w") as f:
                f.write(self.lib.base64_encode("FAKE_SIGNATURE_BY_HACKER"))
        else:
            if not os.path.exists(self.cert_path):
                print(f"📄 [Client] 本地无证书，正在向 CA 申请...")
                self.cert_client.get_certificate()

        # 下载 CA 公钥
        self.ca_pub_path = os.path.join("ca_keys", "ca_public_key.pem")
        if not os.path.exists(self.ca_pub_path):
             Path("ca_keys").mkdir(exist_ok=True)
             self.cert_client.fetch_ca_public_key(self.ca_pub_path)

    def connect_and_send(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"\n🚀 [{'Hacker' if self.is_hacker else 'Client'}] 开始连接服务器...")
            sock.connect((SERVER_HOST, SERVER_PORT))
            
            # 1. 接收 Server 公钥
            data = json.loads(sock.recv(8192).decode("utf-8"))
            server_pub_str = data["public_key"]
            temp_srv_key = os.path.join(KEYS_DIR, "temp_server_key.pem")
            with open(temp_srv_key, "w") as f: f.write(server_pub_str)

            # 2. 发送 {公钥, 证书, DES Key}
            des_key = "SECRETPW" 
            enc_des_key = self.lib.rsa_encrypt(des_key, temp_srv_key)
            
            with open(self.cert_client.pub_path, "r") as f: my_pub = f.read()
            with open(self.cert_path, "r") as f: my_cert = f.read()
            
            sock.sendall(json.dumps({
                "public_key": my_pub,
                "certificate": my_cert,
                "encrypted_des_key": enc_des_key
            }).encode("utf-8"))

            # 3. 等待鉴别结果
            resp_raw = sock.recv(1024).decode("utf-8")
            resp = json.loads(resp_raw)
            
            if resp.get("status") == "error":
                print(f"❌ [{'Hacker' if self.is_hacker else 'Client'}] 被服务器踢出！原因: {resp.get('msg')}")
                return # 连接结束

            print(f"✅ [{'Client'}] 身份验证通过，进入加密通信模式。")
            
            # 4. 发送加密消息
            # ============ 关键修改：可视化密文 ============
            enc_msg = self.lib.des_encrypt(message, des_key)
            print(f"🔒 [Client] 明文: '{message}' -> 加密为: {enc_msg[:30]}...")
            print(f"📤 [Client] 发送密文...")
            sock.sendall(enc_msg.encode("utf-8"))

            # 5. 接收回显
            reply = sock.recv(4096).decode("utf-8")
            print(f"📩 [Client] 收到回显: {self.lib.des_decrypt(reply, des_key)}")

        except Exception as e:
            print(f"⚠️ 发生错误: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    # 默认为合法用户
    client = SecureTcpClient("user_test")
    client.connect_and_send("Hello World")