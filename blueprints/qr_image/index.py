import os
import uuid
import qrcode
from flask import Blueprint, request

# 定义蓝图
qr_image_bp = Blueprint('qrcode', __name__, url_prefix='/qrcode')

# 创建存储二维码图片的文件夹
if not os.path.exists('static/qr_codes'):
	os.makedirs('static/qr_codes')


# 生成有关图片的二维码, 返回的是一个二维码图片的url(服务器地址),
# 该接口需要接收一个参数img_url, 即图片的url
@qr_image_bp.route('/generate_qr', methods=['POST'])
def generate_qr():
	img_url = request.form.get('img_url')


	# 生成二维码
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=10,
		border=4,
	)
	qr.add_data(img_url)
	qr.make(fit=True)
	img = qr.make_image(fill='black', back_color='white')


	# 使用UUID生成唯一文件名
	filename = f"{uuid.uuid4()}.png"
	qr_code_path = os.path.join('static/qr_codes', filename)
	# 保存二维码图片
	img.save(qr_code_path)

	# static/qr_codes\qr_code.png

	return {
		'code':200,
		'image_url':f"http://127.0.0.1:5000/static/qr_codes/{filename}"
	}
