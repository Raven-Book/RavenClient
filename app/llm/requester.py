from typing import Optional

import aiohttp

from app.logger import logger
from app.data import app_data


async def post_request(
        prompt: str,
        api_url: str,
        api_key: str,
        model_id: str,
        max_tokens: int = 500,
        temperature: float = 0.7
) -> Optional[str]:
    """
    调用OpenAI格式API的通用函数

    参数：
    :param prompt: 输入的文本提示
    :param api_url: API端点URL（需包含完整路径，如/v1/chat/completions）
    :param api_key: API认证密钥
    :param model_id: 模型标识符
    :param max_tokens: 生成的最大token数（默认500）
    :param temperature: 生成多样性控制（0-2，默认0.7）

    返回：
    :return: 生成的文本内容 或 None（发生错误时）
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model_id,
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        async with app_data.client as session:
            async with session.post(
                    api_url,
                    headers=headers,
                    json=payload
            ) as response:

                # 检查HTTP状态码
                if response.status != 200:
                    logger.error(f"API请求失败，状态码：{response.status}")
                    return None

                response_data = await response.json()

                # 检查是否存在预期的响应结构
                if "choices" not in response_data or len(response_data["choices"]) == 0:
                    logger.error("无效的API响应结构")
                    logger.error("完整响应：", response_data)
                    return None

                if (response_data.get("choices") and
                        isinstance(response_data["choices"], list) and
                        response_data["choices"][0].get("message") and
                        isinstance(response_data["choices"][0]["message"], dict)):
                    return response_data["choices"][0]["message"].get("content")
    except aiohttp.ClientError as e:
        logger.error(f"网络请求异常：{str(e)}")
    except ValueError as e:
        logger.error(f"JSON解析失败：{str(e)}")
    except Exception as e:
        logger.error(f"未知错误：{str(e)}")

    return None
