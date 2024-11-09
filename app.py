import datetime
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# 导入配置文件
import config

# 导入数据库扩展
from extensions import db

# 导入路由（蓝图）
from blueprints.wallpaper.index import wallpaper_bp
from blueprints.tags.index import tag_bp
from blueprints.user.index import user_bp
from blueprints.qr_image.index import qr_image_bp
from blueprints.post.index import post_bp
from blueprints.topic.index import topic_bp
from blueprints.verify.index import verify_bp
# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置应用
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config.from_object(config)

# CORS配置，允许来自特定来源的请求
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# JWT配置
jwt_manager = JWTManager(app)
# JWT过期时间 为 1星期
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=7)

# 处理token过期
@jwt_manager.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_data):
    return jsonify({'message': 'Token expired', 'code': 401}), 401

# 注册蓝图
app.register_blueprint(wallpaper_bp)
app.register_blueprint(tag_bp)
app.register_blueprint(user_bp)
app.register_blueprint(qr_image_bp)
app.register_blueprint(post_bp)
app.register_blueprint(topic_bp)
app.register_blueprint(verify_bp)
# 配置图片上传路径
app.config['UPLOAD_FOLDER'] = 'uploads/wallpapers'

# 设置静态文件的 URL 路径
app.static_url_path = '/static'

# 初始化数据库
db.init_app(app)
migrate = Migrate(app, db)

# 运行应用
if __name__ == '__main__':
    app.run(debug=True)
