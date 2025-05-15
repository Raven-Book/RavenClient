import base64
import datetime
import hashlib
import hmac
import json
from typing import Any, Dict, Optional, List, Callable

import bcrypt
from fastapi import Request
from starlette import status
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app import model
from app.data import app_data
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


def verify_access_token(secret_key: str, token: str) -> Optional[Dict[str, Any]]:
    """ 验证TOKEN是否过期并且返回Payload """
    payload = get_payload(secret_key, token)

    if not payload:
        return None

    exp_str = payload['exp']
    if not exp_str:
        return None

    try:
        exp = datetime.datetime.fromisoformat(exp_str)

        if exp.tzinfo:
            current = datetime.datetime.now(exp.tzinfo)
        else:
            current = datetime.datetime.now()

        if current > exp:
            logger.debug(f"Token has expired: {token}")
            return None

    except Exception as e:
        logger.error(f"Failed to verify access token: {e}")
        return None

    return payload


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, exclude_paths: List[str]):
        super().__init__(app)
        self.exclude_paths = exclude_paths

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        token: Optional[str] = None
        path = request.url.path

        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")

        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=model.Response(
                    message="Invalid authentication credentials",
                    success=False
                ).model_dump()
            )

        try:
            result = verify_access_token(app_data.config.secret, token)
            if result:
                return await call_next(request)
        except Exception as e:
            logger.error(f"Failed to verify access token: {str(e)}")

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=model.Response(
                    message="Failed to verify access token",
                    success=False
                ).model_dump()
            )

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=model.Response(
                    message="Invalid authentication credentials",
                    success=False
                ).model_dump()
        )

