import base64
import hashlib
import hmac
import json
from typing import Any, Dict, Optional

import bcrypt

from app.logger import logger


def _base64_encode(data):
    if isinstance(data, Dict):
        data = json.dumps(data).encode('utf-8')
    elif isinstance(data, str):
        data = data.encode('utf-8')

    return base64.b64encode(data).decode('utf-8')


def _base64_decode(data):
    return base64.b64decode(data).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"密码验证失败: {str(e)}")
        return False


def generate_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def generate_access_token(secret_key: str, payload: Dict[str, Any]) -> str:
    """ 生成令牌 """
    encoded_header = _base64_encode({"alg": "HS256", "typ": "JWT"})
    encoded_payload = _base64_encode(payload)

    message = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return f"{message}.{signature}"


def get_payload(secret_key: str, token: str) -> Optional[Dict[str, Any]]:
    """ 获取 payload """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        encoded_header, encoded_payload, signature = parts
        message = f"{encoded_header}.{encoded_payload}"

        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload = _base64_decode(encoded_payload)

        return json.loads(payload)
    except Exception as e:
        logger.error(f"Failed to verify access token: {str(e)}")
        return None
