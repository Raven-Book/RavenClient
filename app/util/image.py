from PIL import Image
import base64
import io

from app.logger import logger


def image_to_base64(
        image_path: str,
        max_size: tuple[int, int] = None,
        quality: int = 85,
        format: str = "JPEG"
) -> str:
    """
    将图片转换为 Base64 字符串并支持压缩

    参数：
    :param image_path: 图片文件路径
    :param max_size: 最大尺寸 (宽, 高)，默认不调整大小
    :param quality: 压缩质量 (1-100)，仅对 JPEG 有效
    :param format: 输出格式 (JPEG/PNG)

    返回：
    :return: Base64 编码字符串
    """
    try:
        # 打开并处理图片
        with Image.open(image_path) as img:
            # 调整图片尺寸
            if max_size:
                img.thumbnail(max_size)

            # 转换为 RGB 模式（兼容 JPEG）
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 保存到内存缓冲区
            buffer = io.BytesIO()
            save_args = {'format': format}
            if format == 'JPEG':
                save_args['quality'] = quality
                save_args['optimize'] = True
            elif format == 'PNG':
                save_args['optimize'] = True

            img.save(buffer, **save_args)

            # 生成 Base64
            return base64.b64encode(buffer.getvalue()).decode('utf-8')

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        return ""