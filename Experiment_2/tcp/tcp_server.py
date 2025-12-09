#!/usr/bin/env python3
import socket
import threading
import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from secure_comm_lib import SecureCommLib

HOST = "0.0.0.0"
PORT = 50000
SERVER_DIR = "server_data"
CA_PUB_KEY = "ca_keys/ca_public_key.pem"

class SecureTcpServer:
    def __init__(self):
        self.lib = SecureCommLib()
        Path(SERVER_DIR).mkdir(exist_ok=True)
        self.priv_path = os.path.join(SERVER_DIR, "server_private.pem")
        self.pub_path = os.path.join(SERVER_DIR, "server_public.pem")
        
        if not os.path.exists(self.priv_path):
            self.lib.generate_rsa_keypair(key_dir=SERVER_DIR)
            os.rename(os.path.join(SERVER_DIR, "private_key.pem"), self.priv_path)
            os.rename(os.path.join(SERVER_DIR, "public_key.pem"), self.pub_path)

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"✅ [Server] 安全文件服务器启动 (TCP {HOST}:{PORT})")
        print("ℹ️  [Server] 等待安全连接...")
        
        while True:
            conn, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        print(f"\n🔗 [Server] 客户端 {addr} 尝试连接...")
        try:
            # 1. 发送服务器公钥
            with open(self.pub_path, "r") as f: server_pub = f.read()
            conn.sendall(json.dumps({"public_key": server_pub}).encode("utf-8"))

            # 2. 接收客户端握手包
            data = json.loads(conn.recv(8192).decode("utf-8"))
            client_pub = data["public_key"]
            client_cert = data["certificate"]
            enc_des_key = data["encrypted_des_key"]

            # ============ 关键修改：CA 验证展示 ============
            print(f"🔍 [Server] 正在向 CA 验证客户端证书...")
            ca_key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", CA_PUB_KEY))
            
            # 验证签名：证明该公钥确实是由 CA 签发的
            if not self.lib.verify_signature(client_pub, client_cert, ca_key_path):
                print(f"❌ [Server] 警告：证书验证失败！客户端可能是黑客伪装。")
                print(f"🚫 [Server] 拒绝连接。")
                conn.sendall(json.dumps({"status": "error", "msg": "Certificate Verification Failed"}).encode("utf-8"))
                conn.close()
                return
            else:
                print(f"✅ [Server] 证书验证通过，客户端身份合法。")
            # ============================================

            # 4. 解密 DES 密钥
            des_key = self.lib.rsa_decrypt(enc_des_key, self.priv_path)
            print(f"🔑 [Server] 成功解密 DES 会话密钥")

            # 5. 端点鉴别 (MD5)
            auth_challenge = "ServerAuthRequest"
            md5_val = self.lib.md5_digest(auth_challenge)
            conn.sendall(json.dumps({"status": "ok", "challenge": auth_challenge, "md5": md5_val}).encode("utf-8"))

            while True:
                encrypted_msg = conn.recv(4096).decode("utf-8")
                if not encrypted_msg: break
                
                # ============ 关键修改：可视化密文 ============
                print(f"👀 [网络嗅探] Server 收到密文: {encrypted_msg[:30]}...")
                
                msg = self.lib.des_decrypt(encrypted_msg, des_key)
                print(f"🔓 [Server] 解密后明文: {msg}")
                
                reply = f"Server收到: {msg}"
                conn.sendall(self.lib.des_encrypt(reply, des_key).encode("utf-8"))

        except Exception as e:
            print(f"⚠️ [Server] 连接异常: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    SecureTcpServer().start()