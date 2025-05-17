from PIL import Image
import base64
import io
import cv2
import numpy as np

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
        # 使用 OpenCV 读取图片进行预处理和压缩
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            raise ValueError("无法读取图片文件")

        # 调整图片尺寸
        if max_size:
            img_cv = cv2.resize(img_cv, max_size, interpolation=cv2.INTER_AREA)

        # 转换为 RGB 模式（兼容 JPEG）
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

        # 转换为 PIL 图像
        img_pil = Image.fromarray(img_cv)

        # 保存到内存缓冲区
        buffer = io.BytesIO()
        save_args = {'format': format}
        if format == 'JPEG':
            save_args['quality'] = quality
            save_args['optimize'] = True
        elif format == 'PNG':
            save_args['optimize'] = True

        img_pil.save(buffer, **save_args)

        # 生成 Base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        return ""


def base64_to_image(base64_str: str, output_path: str):
    """
    将 Base64 字符串转换回图片并保存

    参数：
    :param base64_str: Base64 编码的图片字符串
    :param output_path: 输出图片文件路径

    返回：
    :return: None
    """
    try:
        # 解码 Base64
        img_data = base64.b64decode(base64_str)

        # 使用 OpenCV 处理解码后的数据
        img_np = np.frombuffer(img_data, dtype=np.uint8)
        img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if img_cv is None:
            raise ValueError("解码 Base64 数据失败")

        # 保存图片
        cv2.imwrite(output_path, img_cv)
        logger.info(f"图片已保存至: {output_path}")

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
