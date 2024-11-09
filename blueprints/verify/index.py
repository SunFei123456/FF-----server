# 创建蓝图
import os
from flask import Blueprint, jsonify, request

from utils.image_moderation import ImageModeration


verify_bp = Blueprint('verify', __name__, url_prefix='/verify')

# 从环境变量中读取凭据
APPID = os.getenv("APPID")
API_SECRET = os.getenv("API_SECRET")
API_KEY = os.getenv("API_KEY")

# 初始化 ImageModeration 服务
moderation_service = ImageModeration(APPID, API_KEY, API_SECRET)

@verify_bp.route('/moderate-image', methods=['POST'])
def moderate_image():
    """
    使用 ImageModeration 服务审核图像。
    
    :param image_url: 要审核的图像 URL
    :return: 审核结果或错误消息
    """
    data = request.json
    image_url = data.get('image_url')
    if not image_url:
        return jsonify({"error": "未提供图片 URL"}), 400
    try:
        response = moderation_service.image_moderate(image_url)
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500