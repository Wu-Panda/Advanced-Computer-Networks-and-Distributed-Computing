# 文件路径: Experiment_2/udp/udp_client.py
#!/usr/bin/env python3
import socket
import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from secure_comm_lib import SecureCommLib

CA_HOST = "127.0.0.1"
CA_PORT = 50001
KEYS_DIR = "client_keys"

class CertificateClient:
    def __init__(self, user_id):
        self.user_id = user_id
        self.lib = SecureCommLib()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(5)
        self._init_keys()

    def _init_keys(self):
        Path(KEYS_DIR).mkdir(exist_ok=True)
        self.priv_path = os.path.join(KEYS_DIR, f"{self.user_id}_private.pem")
        self.pub_path = os.path.join(KEYS_DIR, f"{self.user_id}_public.pem")
        if not os.path.exists(self.priv_path):
            self.lib.generate_rsa_keypair(key_dir=KEYS_DIR)
            os.rename(os.path.join(KEYS_DIR, "private_key.pem"), self.priv_path)
            os.rename(os.path.join(KEYS_DIR, "public_key.pem"), self.pub_path)

    def get_certificate(self):
        """向 CA 申请证书并保存"""
        with open(self.pub_path, "r") as f:
            pub_key = f.read()
        
        req = {"action": "register", "user_id": self.user_id, "public_key": pub_key}
        self.socket.sendto(json.dumps(req).encode("utf-8"), (CA_HOST, CA_PORT))
        
        try:
            data, _ = self.socket.recvfrom(8192)
            resp = json.loads(data.decode("utf-8"))
            if resp["status"] == "ok":
                cert_path = os.path.join(KEYS_DIR, f"{self.user_id}_cert.sig")
                with open(cert_path, "w") as f:
                    f.write(resp["certificate"])
                print(f"[Client] 证书获取成功，已保存至 {cert_path}")
                return True
        except socket.timeout:
            print("[Client] 连接 CA 超时")
        return False

    def fetch_ca_public_key(self, save_path):
        """获取 CA 公钥用于后续验证"""
        req = {"action": "get_ca_key"}
        self.socket.sendto(json.dumps(req).encode("utf-8"), (CA_HOST, CA_PORT))
        data, _ = self.socket.recvfrom(8192)
        resp = json.loads(data.decode("utf-8"))
        if resp["status"] == "ok":
            with open(save_path, "w") as f:
                f.write(resp["public_key"])

if __name__ == "__main__":
    client = CertificateClient("test_user")
    client.get_certificate()