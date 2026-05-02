插件签名验证服务
- 验证官方插件的完整性与来源真实性
- 支持多签名者（Falck 独特性签名）
- RSA-SHA256 非对称加密方案

import os
import json
import hashlib
import base64
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

from oss.plugin.types import Plugin
from oss.config import get_config


FALCK_PUBLIC_KEY_PEM = 

NEBULASHELL_PUBLIC_KEY_PEM = 


class SignatureError(Exception):

    def __init__(self, key_dir: str = None):
        config = get_config()
        self.key_dir = Path(key_dir or str(config.get("SIGNATURE_KEYS_DIR", "./data/signature-verifier/keys")))
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.public_keys: Dict[str, bytes] = {}
        self._load_builtin_keys()

    def _load_builtin_keys(self):
        pub_dir = self.key_dir / "public"
        if not pub_dir.exists():
            return
        for key_file in pub_dir.glob("*.pem"):
            author_name = key_file.stem
            self.public_keys[author_name] = key_file.read_bytes()

    def _compute_plugin_hash(self, plugin_dir: Path) -> str:
        计算插件目录的内容哈希
        包含所有文件的路径相对路径 + 内容
        hasher = hashlib.sha256()
        
        files_to_hash = []
        for file_path in sorted(plugin_dir.rglob("*")):
            if file_path.is_file() and file_path.name != "SIGNATURE":
                rel_path = file_path.relative_to(plugin_dir)
                files_to_hash.append((str(rel_path), file_path))
        
        for rel_path, file_path in files_to_hash:
            hasher.update(rel_path.encode("utf-8"))
            hasher.update(file_path.read_bytes())
        
        return hasher.hexdigest()

    def verify_plugin(self, plugin_dir: Path, author: str = "Falck") -> Tuple[bool, str]:
        验证插件签名
        返回: (是否有效, 详细信息)
        signature_file = plugin_dir / "SIGNATURE"
        
        if not signature_file.exists():
            return False, f"插件缺少签名文件: {plugin_dir}"
        
        try:
            sig_data = json.loads(signature_file.read_text())
        except json.JSONDecodeError as e:
            return False, f"签名文件格式错误: {e}"
        
        required_fields = ["signature", "signer", "algorithm", "timestamp"]
        for field in required_fields:
            if field not in sig_data:
                return False, f"签名文件缺少必需字段: {field}"
        
        signer = sig_data["signer"]
        signature = base64.b64decode(sig_data["signature"])
        
        if signer not in self.public_keys:
            return False, f"未知签名者: {signer}"
        
        try:
            public_key = serialization.load_pem_public_key(
                self.public_keys[signer],
                backend=default_backend()
            )
        except Exception as e:
            return False, f"公钥加载失败: {e}"
        
        current_hash = self._compute_plugin_hash(plugin_dir)
        
        try:
            signed_data = f"{author}:{current_hash}".encode("utf-8")
            public_key.verify(
                signature,
                signed_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True, f"签名验证通过 (签名者: {signer})"
        except InvalidSignature:
            return False, f"签名不匹配！插件可能已被篡改 (签名者: {signer})"
        except Exception as e:
            return False, f"签名验证异常: {e}"

    def is_official_plugin(self, plugin_dir: Path) -> bool:

    def __init__(self, private_key_path: Optional[str] = None):
        self.private_key = None
        if private_key_path:
            self.load_private_key(private_key_path)

    def load_private_key(self, key_path: str):
        self.private_key = serialization.load_pem_private_key(
            pem_data.encode(),
            password=None,
            backend=default_backend()
        )

    def sign_plugin(self, plugin_dir: Path, signer_name: str, author: str = "Falck") -> str:
        为插件生成签名
        返回: 签名的文件路径
        if not self.private_key:
            raise ValueError("未加载私钥")
        
        hasher = hashlib.sha256()
        files_to_hash = []
        for file_path in sorted(plugin_dir.rglob("*")):
            if file_path.is_file() and file_path.name not in ("SIGNATURE",):
                rel_path = file_path.relative_to(plugin_dir)
                files_to_hash.append((str(rel_path), file_path))
        
        for rel_path, file_path in files_to_hash:
            hasher.update(rel_path.encode("utf-8"))
            hasher.update(file_path.read_bytes())
        
        plugin_hash = hasher.hexdigest()
        
        import time
        signed_data = f"{author}:{plugin_hash}".encode("utf-8")
        signature = self.private_key.sign(
            signed_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        sig_data = {
            "signature": base64.b64encode(signature).decode(),
            "signer": signer_name,
            "algorithm": "RSA-SHA256",
            "timestamp": time.time(),
            "plugin_hash": plugin_hash,
            "author": author
        }
        
        signature_file = plugin_dir / "SIGNATURE"
        signature_file.write_text(json.dumps(sig_data, indent=2))
        
        return str(signature_file)


class SignatureVerifierPlugin(Plugin):
        return self.verifier.verify_plugin(plugin_dir, author)

    def is_official(self, plugin_dir: Path) -> bool:
        if not self.signer:
            raise SignatureError("未加载私钥，无法签名")
        return self.signer.sign_plugin(plugin_dir, signer_name, author)

    def generate_keypair(self, author: str, key_dir: str = None):
