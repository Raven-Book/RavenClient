from typing import Optional

import bcrypt

from app.logger import logger


def generate_password_hash(password: str) -> Optional[bytes]:
    """安全生成密码哈希（包含自动生成的盐）"""
    try:
        if not password:
            raise ValueError("密码不能为空")

        # 将密码字符串转换为bytes
        password_bytes = password.encode('utf-8')

        # 生成带盐的哈希值
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt(12))
    except Exception as e:
        # 实际应用中应记录日志
        logger.error(f"生成密码哈希失败: {str(e)}")
        return None


def check_password_hash(password: str, hashed: bytes) -> bool:
    """安全验证密码与哈希是否匹配"""
    try:
        if not password or not hashed:
            return False

        password_bytes = password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed)
    except (ValueError, TypeError) as e:
        # 处理无效哈希或类型错误
        logger.info(f"密码验证异常: {str(e)}")
        return False