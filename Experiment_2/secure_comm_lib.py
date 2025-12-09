# 文件路径: Experiment_2/secure_comm_lib.py
import base64
import hashlib
import json
import os
import pyDes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Sig_PK
from Crypto.Hash import SHA256

class SecureCommLib:
    """
    安全通信核心库
    实现了 PDF 文档要求的 DES 加密、RSA 密钥生成/加解密/签名、MD5 摘要与 Base64 转码
    """
    
    def generate_rsa_keypair(self, key_size=2048, key_dir="keys"):
        """生成 RSA 密钥对并保存到文件 [cite: 32, 42]"""
        if not os.path.exists(key_dir):
            os.makedirs(key_dir)
            
        key = RSA.generate(key_size)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        
        with open(os.path.join(key_dir, "private_key.pem"), "wb") as f:
            f.write(private_key)
        with open(os.path.join(key_dir, "public_key.pem"), "wb") as f:
            f.write(public_key)
        return private_key, public_key

    def rsa_encrypt(self, message: str, public_key_path: str) -> str:
        """RSA 公钥加密 (用于 DES 密钥共享) [cite: 75, 94]"""
        with open(public_key_path, "r") as f:
            key = RSA.import_key(f.read())
        cipher = PKCS1_v1_5.new(key)
        # 必须分块或确保消息短于密钥长度，这里用于加密 DES Key (很短)
        encrypted_bytes = cipher.encrypt(message.encode("utf-8"))
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    def rsa_decrypt(self, b64_encrypted_msg: str, private_key_path: str) -> str:
        """RSA 私钥解密 [cite: 27]"""
        with open(private_key_path, "r") as f:
            key = RSA.import_key(f.read())
        cipher = PKCS1_v1_5.new(key)
        encrypted_bytes = base64.b64decode(b64_encrypted_msg)
        sentinel = object() # 解密失败时的哨兵对象
        decrypted_msg = cipher.decrypt(encrypted_bytes, sentinel)
        if decrypted_msg is sentinel:
            raise ValueError("RSA decryption failed")
        return decrypted_msg.decode("utf-8")

    def des_encrypt(self, text: str, key: str) -> str:
        """DES 加密 (使用 pyDes, CBC 模式) [cite: 12, 14]"""
        # 确保 key 是 8 字节
        k = pyDes.des(key[:8].encode(), pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
        encrypted_bytes = k.encrypt(text.encode("utf-8"))
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    def des_decrypt(self, b64_text: str, key: str) -> str:
        """DES 解密 [cite: 17, 19]"""
        k = pyDes.des(key[:8].encode(), pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
        encrypted_bytes = base64.b64decode(b64_text)
        return k.decrypt(encrypted_bytes).decode("utf-8")

    def md5_digest(self, data: str) -> str:
        """计算 MD5 摘要 (用于端点鉴别) """
        return hashlib.md5(data.encode("utf-8")).hexdigest()

    def sign_data(self, data: str, private_key_path: str) -> str:
        """数字签名 (RSA 私钥签名) [cite: 28]"""
        with open(private_key_path, "r") as f:
            key = RSA.import_key(f.read())
        h = SHA256.new(data.encode("utf-8"))
        signer = Sig_PK.new(key)
        signature = signer.sign(h)
        return base64.b64encode(signature).decode("utf-8")

    def verify_signature(self, data: str, b64_signature: str, public_key_path: str) -> bool:
        """验证数字签名 (RSA 公钥验签) [cite: 28]"""
        with open(public_key_path, "r") as f:
            key = RSA.import_key(f.read())
        h = SHA256.new(data.encode("utf-8"))
        verifier = Sig_PK.new(key)
        try:
            signature = base64.b64decode(b64_signature)
            return verifier.verify(h, signature)
        except (ValueError, TypeError):
            return False

    def base64_encode(self, data: str) -> str:
        """Base64 编码辅助"""
        return base64.b64encode(data.encode("utf-8")).decode("utf-8")

    def base64_decode(self, data: str) -> str:
        """Base64 解码辅助"""
        return base64.b64decode(data).decode("utf-8")
        
    def issue_certificate(self, user_public_key: str, ca_private_key_path: str) -> str:
        """CA 签发证书：对用户公钥进行签名"""
        # 证书内容就是对“用户公钥”的签名
        return self.sign_data(user_public_key, ca_private_key_path)