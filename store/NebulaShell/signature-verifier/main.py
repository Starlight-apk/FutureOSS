"""
Plugin Signature Verification Service
- Verify integrity and origin authenticity of official plugins
- Support multiple signers (Falck unique signature)
- RSA-SHA256 asymmetric encryption scheme
"""

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


FALCK_PUBLIC_KEY_PEM = ""

NEBULASHELL_PUBLIC_KEY_PEM = ""


class SignatureError(Exception):
    pass


class SignatureVerifier:
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
        """Compute content hash of the plugin directory.
        Includes relative path + content of all files.
        """
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
        """Verify plugin signature.
        Returns: (is_valid, details)
        """
        signature_file = plugin_dir / "SIGNATURE"
        
        if not signature_file.exists():
            return False, f"Plugin missing signature file: {plugin_dir}"
        
        try:
            sig_data = json.loads(signature_file.read_text())
        except json.JSONDecodeError as e:
            return False, f"Signature file format error: {e}"
        
        required_fields = ["signature", "signer", "algorithm", "timestamp"]
        for field in required_fields:
            if field not in sig_data:
                return False, f"Signature missing required field: {field}"
        
        signer = sig_data["signer"]
        signature = base64.b64decode(sig_data["signature"])
        
        if signer not in self.public_keys:
            return False, f"Unknown signer: {signer}"
        
        try:
            public_key = serialization.load_pem_public_key(
                self.public_keys[signer],
                backend=default_backend()
            )
        except Exception as e:
            return False, f"Public key load failed: {e}"
        
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
            return True, f"Signature verified (signer: {signer})"
        except InvalidSignature:
            return False, f"Signature mismatch! Plugin may have been tampered with (signer: {signer})"
        except Exception as e:
            return False, f"Signature verification error: {e}"

    def is_official_plugin(self, plugin_dir: Path) -> bool:
        pass


class PluginSigner:
    def __init__(self, private_key_path: Optional[str] = None):
        self.private_key = None
        if private_key_path:
            self.load_private_key(private_key_path)

    def load_private_key(self, key_path: str):
        with open(key_path, "rb") as f:
            pem_data = f.read()
        self.private_key = serialization.load_pem_private_key(
            pem_data,
            password=None,
            backend=default_backend()
        )

    def sign_plugin(self, plugin_dir: Path, signer_name: str, author: str = "Falck") -> str:
        """Generate signature for a plugin.
        Returns: path to the signature file
        """
        if not self.private_key:
            raise ValueError("Private key not loaded")
        
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
    def __init__(self):
        self.verifier = SignatureVerifier()
        self.signer = None

    def verify(self, plugin_dir: Path, author: str = "Falck") -> Tuple[bool, str]:
        return self.verifier.verify_plugin(plugin_dir, author)

    def is_official(self, plugin_dir: Path) -> bool:
        return self.verifier.is_official_plugin(plugin_dir)

    def sign(self, plugin_dir: Path, signer_name: str, author: str = "Falck") -> str:
        if not self.signer:
            raise SignatureError("Private key not loaded, cannot sign")
        return self.signer.sign_plugin(plugin_dir, signer_name, author)

    def generate_keypair(self, author: str, key_dir: str = None):
        pass
