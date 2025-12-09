#!/usr/bin/env python3
import socket
import json
import os
import sys
from pathlib import Path

# 路径修正
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from secure_comm_lib import SecureCommLib

HOST = "0.0.0.0"
CA_PORT = 50001
KEYS_DIR = "ca_keys"

class CAServer:
    def __init__(self):
        self.socket = None
        self.lib = SecureCommLib()
        self._init_ca_keys()

    def _init_ca_keys(self):
        Path(KEYS_DIR).mkdir(exist_ok=True)
        self.ca_private_key_path = os.path.join(KEYS_DIR, "ca_private_key.pem")
        self.ca_public_key_path = os.path.join(KEYS_DIR, "ca_public_key.pem")
        
        if not os.path.exists(self.ca_private_key_path):
            print("[CA中心] 正在初始化根密钥...")
            self.lib.generate_rsa_keypair(key_dir=KEYS_DIR)
            os.rename(os.path.join(KEYS_DIR, "private_key.pem"), self.ca_private_key_path)
            os.rename(os.path.join(KEYS_DIR, "public_key.pem"), self.ca_public_key_path)

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((HOST, CA_PORT))
        print(f"✅ [CA中心] 服务启动成功 (UDP {HOST}:{CA_PORT})")
        print(f"ℹ️  [CA中心] 等待证书申请...")
        
        while True:
            try:
                data, addr = self.socket.recvfrom(8192)
                request = json.loads(data.decode("utf-8"))
                response = self._handle_request(request)
                self.socket.sendto(json.dumps(response).encode("utf-8"), addr)
            except Exception as e:
                print(f"❌ [CA中心] 错误: {e}")

    def _handle_request(self, request):
        action = request.get("action")
        if action == "register":
            user_id = request.get("user_id")
            print(f"📩 [CA中心] 收到用户 '{user_id}' 的公钥，正在签署证书...")
            signature = self.lib.issue_certificate(request.get("public_key"), self.ca_private_key_path)
            return {"status": "ok", "user_id": user_id, "certificate": signature}
        elif action == "get_ca_key":
            with open(self.ca_public_key_path, 'r') as f:
                return {"status": "ok", "public_key": f.read()}
        return {"status": "error", "message": "Unknown action"}

if __name__ == "__main__":
    CAServer().start()