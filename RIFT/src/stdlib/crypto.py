"""
RIFT Standard Library - Crypto Module

Encryption, hashing, and security utilities.
"""

import os
import hashlib
import hmac
import base64
import secrets
import uuid as uuid_module
from typing import Any, Dict, Optional, Tuple


def create_crypto_module(interpreter) -> Dict[str, Any]:
    """Create the crypto module for RIFT."""
    
    # ========================================================================
    # Symmetric Encryption (AES-256-GCM)
    # ========================================================================
    
    def crypto_encrypt(data: str, key: str) -> str:
        """Encrypt data using AES-256-GCM."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            # Derive 256-bit key from password
            key_bytes = hashlib.sha256(key.encode()).digest()
            
            # Generate random nonce
            nonce = os.urandom(12)
            
            # Encrypt
            aesgcm = AESGCM(key_bytes)
            ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
            
            # Return base64 encoded nonce + ciphertext
            return base64.b64encode(nonce + ciphertext).decode()
        except ImportError:
            raise ImportError("cryptography library required for encryption")
    
    def crypto_decrypt(encrypted: str, key: str) -> str:
        """Decrypt data using AES-256-GCM."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            # Derive key
            key_bytes = hashlib.sha256(key.encode()).digest()
            
            # Decode
            data = base64.b64decode(encrypted)
            nonce = data[:12]
            ciphertext = data[12:]
            
            # Decrypt
            aesgcm = AESGCM(key_bytes)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode()
        except ImportError:
            raise ImportError("cryptography library required for decryption")
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    # ========================================================================
    # Asymmetric Encryption (RSA)
    # ========================================================================
    
    def crypto_keypair(bits: int = 2048) -> Dict[str, str]:
        """Generate RSA key pair."""
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=bits
            )
            
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
            
            return {
                'private': private_pem,
                'public': public_pem
            }
        except ImportError:
            raise ImportError("cryptography library required for key generation")
    
    def crypto_encrypt_rsa(data: str, public_key: str) -> str:
        """Encrypt data with RSA public key."""
        try:
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives import hashes, serialization
            
            key = serialization.load_pem_public_key(public_key.encode())
            
            ciphertext = key.encrypt(
                data.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return base64.b64encode(ciphertext).decode()
        except ImportError:
            raise ImportError("cryptography library required for RSA encryption")
    
    def crypto_decrypt_rsa(encrypted: str, private_key: str) -> str:
        """Decrypt data with RSA private key."""
        try:
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives import hashes, serialization
            
            key = serialization.load_pem_private_key(private_key.encode(), password=None)
            
            plaintext = key.decrypt(
                base64.b64decode(encrypted),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return plaintext.decode()
        except ImportError:
            raise ImportError("cryptography library required for RSA decryption")
    
    # ========================================================================
    # Hashing
    # ========================================================================
    
    def crypto_hash(data: str, algorithm: str = 'sha256') -> str:
        """Hash data with specified algorithm."""
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha384': hashlib.sha384,
            'sha512': hashlib.sha512,
        }
        
        if algorithm not in algorithms:
            raise ValueError(f"Unknown hash algorithm: {algorithm}")
        
        hasher = algorithms[algorithm]()
        hasher.update(data.encode())
        return hasher.hexdigest()
    
    def crypto_hash512(data: str) -> str:
        """SHA-512 hash."""
        return crypto_hash(data, 'sha512')
    
    def crypto_hashpass(password: str, rounds: int = 12) -> str:
        """Hash password with bcrypt."""
        try:
            import bcrypt
            salt = bcrypt.gensalt(rounds=rounds)
            hashed = bcrypt.hashpw(password.encode(), salt)
            return hashed.decode()
        except ImportError:
            raise ImportError("bcrypt library required for password hashing")
    
    def crypto_checkpass(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash."""
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except ImportError:
            raise ImportError("bcrypt library required for password verification")
    
    # ========================================================================
    # JWT Support
    # ========================================================================
    
    def crypto_token(payload: Dict, secret: str, algorithm: str = 'HS256',
                     expires_in: Optional[int] = None) -> str:
        """Create JWT token."""
        try:
            import jwt
            import time
            
            token_payload = payload.copy()
            
            if expires_in:
                token_payload['exp'] = int(time.time()) + expires_in
            
            return jwt.encode(token_payload, secret, algorithm=algorithm)
        except ImportError:
            raise ImportError("PyJWT library required for JWT operations")
    
    def crypto_verify(token: str, secret: str, algorithms: list = None) -> Dict:
        """Verify and decode JWT token."""
        try:
            import jwt
            
            if algorithms is None:
                algorithms = ['HS256']
            
            return jwt.decode(token, secret, algorithms=algorithms)
        except ImportError:
            raise ImportError("PyJWT library required for JWT operations")
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")
    
    # ========================================================================
    # Random Generation
    # ========================================================================
    
    def crypto_random(length: int = 32) -> str:
        """Generate cryptographically secure random string."""
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def crypto_random_bytes(length: int = 32) -> str:
        """Generate random bytes (hex encoded)."""
        return secrets.token_hex(length)
    
    def crypto_random_int(min_val: int = 0, max_val: int = 2**32) -> int:
        """Generate random integer."""
        return secrets.randbelow(max_val - min_val) + min_val
    
    def crypto_uuid() -> str:
        """Generate UUID v4."""
        return str(uuid_module.uuid4())
    
    # ========================================================================
    # HMAC
    # ========================================================================
    
    def crypto_sign(data: str, key: str, algorithm: str = 'sha256') -> str:
        """Create HMAC signature."""
        hash_func = getattr(hashlib, algorithm, None)
        if not hash_func:
            raise ValueError(f"Unknown hash algorithm: {algorithm}")
        
        signature = hmac.new(key.encode(), data.encode(), hash_func)
        return signature.hexdigest()
    
    def crypto_verify_hmac(data: str, signature: str, key: str,
                           algorithm: str = 'sha256') -> bool:
        """Verify HMAC signature."""
        expected = crypto_sign(data, key, algorithm)
        return hmac.compare_digest(expected, signature)
    
    # ========================================================================
    # Encoding/Decoding
    # ========================================================================
    
    def crypto_base64_encode(data: str) -> str:
        """Base64 encode."""
        return base64.b64encode(data.encode()).decode()
    
    def crypto_base64_decode(data: str) -> str:
        """Base64 decode."""
        return base64.b64decode(data).decode()
    
    def crypto_hex_encode(data: str) -> str:
        """Hex encode."""
        return data.encode().hex()
    
    def crypto_hex_decode(data: str) -> str:
        """Hex decode."""
        return bytes.fromhex(data).decode()
    
    return {
        'encrypt': crypto_encrypt,
        'decrypt': crypto_decrypt,
        'keypair': crypto_keypair,
        'encryptRSA': crypto_encrypt_rsa,
        'decryptRSA': crypto_decrypt_rsa,
        'hash': crypto_hash,
        'hash512': crypto_hash512,
        'hashpass': crypto_hashpass,
        'checkpass': crypto_checkpass,
        'token': crypto_token,
        'verify': crypto_verify,
        'random': crypto_random,
        'randomBytes': crypto_random_bytes,
        'randomInt': crypto_random_int,
        'uuid': crypto_uuid,
        'sign': crypto_sign,
        'verifyHMAC': crypto_verify_hmac,
        'base64Encode': crypto_base64_encode,
        'base64Decode': crypto_base64_decode,
        'hexEncode': crypto_hex_encode,
        'hexDecode': crypto_hex_decode,
    }
