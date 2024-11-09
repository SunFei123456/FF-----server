#  编写关于壁纸的路由(蓝图)
import datetime
import os

# 导入Flask类
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from PIL import Image as I  # 导入 Pillow 库来处理图像

# 导入db数据库
from extensions import db
# 导入模型
from model.index import Image, Tag, image_tags, User, user_collect_images, user_favorite_images

# 定义蓝图
wallpaper_bp = Blueprint('wallpaper', __name__, url_prefix='/wallpaper')



@wallpaper_bp.route('/get_hot20', methods=['GET'])
def get_hot_wallpapers():
    # 查询数据库并获取前20张图片，并计算热度值
    images = (Image.query
              .order_by((Image.download_count * 3) + (Image.like_count * 2) + (Image.favorite_count * 1).desc())
              .limit(100).all())

    # 构造返回的JSON数据
    data = []
    for image in images:
        heat_value = (image.download_count * 3) + (image.like_count * 2) + (image.favorite_count * 1)
        data.append({
            'id': image.id,
            'url': image.url,
            'author': image.create_by,  # 这可能需要转换成用户名
            'type': image.type,
            'download_count': image.download_count,
            'like_count': image.like_count,
            'favorite_count': image.favorite_count,
            'heat_value': heat_value  # 包含热度值
        })

    # 返回JSON数据
    return jsonify(data)

# 获取所有壁纸
@wallpaper_bp.route('/get_all', methods=['GET'])
def get_all_wallpapers():
    # 查询数据库并获取所有图片
    images = Image.query.all()
    if images:
        # 构造返回的JSON数据
        data = []
        for image in images:
            # 获取创建者用户信息
            author = User.query.get(image.create_by)
            if author:
                author_info = {
                    'name': author.username,
                    'user_id': author.id,
                    'avatar': author.image
                }
            else:
                author_info = None
            # 解析 create_time 并转换为所需格式
            create_time = image.create_time.strftime('%Y:%m:%d %H:%M')
            data.append({
                'id': image.id,
                'name': image.name,
                'url': image.url,
                'author': author_info,  # 这可能需要转换成用户名
                'type': image.type,
                'file_size_mb': round(image.file_size / 1024 / 1024, 2),
                'dimensions': image.dimensions,
                'download_count': image.download_count,
                'like_count': image.like_count,
                'favorite_count': image.favorite_count,
                'create_time': create_time,
                'status': image.status,
            })
        return jsonify({'code': 200, 'data': data, 'message': '成功获取'})
    else:
        return  jsonify({'message': '找不到壁纸.'})


# 下架壁纸



@wallpaper_bp.route('/tags/<string:tag>', methods=['GET'])
def get_wallpapers_by_tag(tag):
    # 查询标签的 ID
    tag_obj = Tag.query.filter_by(name=tag).first_or_404()
    tag_id = tag_obj.id

    # 查询 image_tags 关联表中的 image_id
    image_ids = [image_tag.image_id for image_tag in db.session.query(image_tags).filter_by(tag_id=tag_id).all()]

    # 根据 image_ids 查询图片信息
    images = Image.query.filter(Image.id.in_(image_ids)).all()

    # 构造返回的 JSON 数据
    data = []
    for image in images:
        data.append({
            'id': image.id,
            'name': image.name,
            'url': image.url,
            'alt': image.alt,
            'type': image.type,
            'file_size': image.file_size,
            'dimensions': image.dimensions,
            'create_by': image.create_by,  # 假设 create_by 是一个 User ID，需要额外查询 User 表来获取用户名
            'create_time': image.create_time,
            'update_time': image.update_time,
            'download_count': image.download_count,
            'like_count': image.like_count,
            'favorite_count': image.favorite_count,
            'tags': [tag.name for tag in image.tags]  # 获取图片的标签名称列表
        })

    return jsonify(data)


# 根据图片id返回图片
@wallpaper_bp.route('/<int:image_id>', methods=['GET'])
def get_wallpaper_by_id(image_id):
    image = Image.query.get(image_id)
    # 如果找不到,
    if  image is None:
        return jsonify({'error': '图片不存在', 'code': 404}), 404


    # 构造返回的JSON数据
    data = {
            'name': image.name,
            'alt': image.alt,
            'id': image.id,
            'url': image.url,
            'author': image.create_by,
            'type': image.type,
            'download_count': image.download_count,
            'like_count': image.like_count,
            'favorite_count': image.favorite_count,
            #  图片的分辨率
            'dimensions' : image.dimensions,
            # 图片的上传时间
            'create_time' : image.create_time,
            # 图片大小: 进行mb的转换, 保留小数点后两位
            'file_size_mb': round(image.file_size/1024/1024, 2),
    }

    # 返回JSON数据
    return jsonify(data)



#  排序模块

## 根据发布时间进行排序 (最新)
@wallpaper_bp.route('/new', methods=['GET'])
def get_new_wallpapers():
    # 获取所有图片
    images = Image.query.all()
    # 按发布时间降序排序
    sorted_images = sorted(images, key=lambda x: x.create_time, reverse=False)
    # 构造返回的JSON数据
    data = []
    for image in sorted_images:
        data.append({
            'id': image.id,
            'url': image.url,
            'alt': image.alt,
            'type': image.type,
            'author': image.create_by,
            'create_time': image.create_time,
            'download_count': image.download_count,
            'like_count': image.like_count,
            'favorite_count': image.favorite_count
        })

    return jsonify(data)



## 根据点赞量排序返回
@wallpaper_bp.route('/like', methods=['GET'])
def get_liked_wallpapers():
    # 获取所有图片
    images = Image.query.all()
    # 按点赞量降序排序
    sorted_images = sorted(images, key=lambda x: x.like_count, reverse=True)
    # 构造返回的JSON数据
    data = []
    for image in sorted_images:
        data.append({
            'id': image.id,
            'url': image.url,
            'alt': image.alt,
            'type': image.type,
            'author': image.create_by,
            'create_time': image.create_time,
            'download_count': image.download_count,
            'like_count': image.like_count,
            'favorite_count': image.favorite_count
        })


    return jsonify(data)


## 根据下载量排序返回
@wallpaper_bp.route('/download', methods=['GET'])
def get_download_wallpapers():
    # 获取所有图片
    images = Image.query.all()
    # 按点赞量降序排序
    sorted_images = sorted(images, key=lambda x: x.download_count, reverse=True)
    # 构造返回的JSON数据
    data = []
    for image in sorted_images:
        data.append({
            'id': image.id,
            'url': image.url,
            'alt': image.alt,
            'type': image.type,
            'author': image.create_by,
            'create_time': image.create_time,
            'download_count': image.download_count,
            'like_count': image.like_count,
            'favorite_count': image.favorite_count
        })


    return jsonify(data)


UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','webp','blob'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 图片上传
@wallpaper_bp.route('/upload', methods=['POST'])
def upload_wallpaper():
    # 拿到前端传过来的图片的数据
    file = request.files.get('file')
    # 打印类型
    print(type(file))
    
    if file and allowed_file(file.filename):
         # filename 使用时间戳命名
        filename =  str(datetime.datetime.now().timestamp()) + secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename) # 拿到上传图片的路径
        file.save(file_path) # 保存图片

        # 获取图片的详细信息
        with I.open(file_path) as img:
            width, height = img.size # 获取分辨率
            file_format = img.format
            mode = img.mode

        file_size = os.path.getsize(file_path)  # 文件大小
        file_type = file.mimetype  # 文件类型
        file_name = file.filename  # 文件名称

        # 整合信息 进行return 返回
        data = {
            'file_path': f'http://127.0.0.1:5000/{file_path}',
            'width': width,
            'height': height,
            'file_format': file_format,
            'mode': mode,
            'file_size': file_size,
            'file_type': file_type,
            'file_name': file_name
        }
        return jsonify(data)
    else:
        return jsonify({'error': 'Invalid file type'}), 400,

# 图片相关信息存储数据库 + 同时设置tag表 将上传的图片的url的id 与当前的tag表的id进行关联
@wallpaper_bp.route('/save', methods=['POST'])
def save_wallpaper():
    # 解析请求数据
    data = request.json
    if not data:
        return jsonify({'error': '没有提供任何数据'}), 400

    name = data.get('name')
    url = data.get('url')
    alt = data.get('alt')
    type = data.get('type')
    width = data.get('width')
    height = data.get('height')
    size = data.get('file_size')
    creator = data.get('create_by')
    tag_id = data.get('tag_id')
    dimensions = f"{width} x {height}"

    # 判断该图片是否已经在数据库存在. 如果存在就进行return返回
    if Image.query.filter_by(url=url).first():
        return jsonify({'error': '图片已存在'}), 400

    # 开始事务
    try:
        # 保存图片对象到数据库
        wallpaper = Image(name=name, url=url, alt=alt, type=type, file_size=size,
                          dimensions=dimensions, create_by=creator)
        db.session.add(wallpaper)
        db.session.flush()  # 刷新会话，以获取图片ID

        # 获取刚插入的图片ID
        image_id = wallpaper.id

        # 关联图片与标签
        tag = Tag.query.get(tag_id)
        if tag:
            wallpaper.tags.append(tag)
            db.session.commit()
            return jsonify({'message': '图片上传成功', 'code': 200}), 200
        else:
            db.session.rollback()  # 回滚事务
            return jsonify({'error': 'Tag not found'}), 404
    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚事务
        return jsonify({'error': str(e)}), 500
    finally:
        db.session.close()

# 模糊查询, 查询wallpaper表name字段中包含关键词的图片
@wallpaper_bp.route('/search', methods=['GET'])
def search_images_by_keyword():
    print(1)
    keyword = request.args.get('keyword', '')
    print("ke",type(keyword))
    print(2)
    if not keyword:
        return jsonify({'error': '请输入关键词'}), 400
    images = Image.query.filter(Image.name.like(f'%{keyword}%').collate('utf8_general_ci')).all()
    print(images)
    if not images:
        return jsonify({'error': '未找到相关图片'}), 404
    image_list = []
    for image in images:
        image_list.append({
            'id': image.id,
            'name': image.name,
            'url': image.url,
            'alt': image.alt,
            'type': image.type,
            'file_size': image.file_size,
            'dimensions': image.dimensions,
            'create_by': image.create_by,
            'create_time': image.create_time
            })


    return jsonify({'images': image_list}), 200



@wallpaper_bp.route('/user_image_relation', methods=['POST'])
def get_image_relation():
    user_id = request.json.get('user_id')
    image_id = request.json.get('image_id')
    try:
        # 查询数据库，检查用户是否存在
        user = User.query.get(user_id)
        if user is None:
            return jsonify({'error': '用户不存在'}), 404

        # 查询数据库，检查图片是否存在
        image = Image.query.get(image_id)
        if image is None:
            return jsonify({'error': '图片不存在'}), 404

        # 检查用户是否喜欢和收藏该图片
        is_collected = image in user.collect_images
        is_liked = image in user.favorite_images

        return jsonify({
            'is_collected': is_collected,
            'is_liked': is_liked
        }), 200

    except Exception as e:
        # 捕获数据库查询错误
        return jsonify({'error': str(e)}), 500


@wallpaper_bp.route('/delete', methods=['POST'])
def delete_image():
    user_id = request.json.get('user_id')
    image_id = request.json.get('image_id')
    
    print("user_id, image_id",user_id, image_id)

    # 检查必需字段
    if not user_id or not image_id:
        return jsonify({'error': 'Missing user_id or image_id'}), 400

    try:
        # 查询数据库，检查用户是否存在
        user = User.query.get(user_id)
        if user is None:
            return jsonify({'error': '用户不存在'}), 404

        # 查询数据库，检查图片是否存在
        image = Image.query.get(image_id)
        if image is None:
            return jsonify({'error': '图片不存在'}), 404

        # 检查用户是否收藏或喜欢了图片
        is_collected = image in user.collect_images
        is_favorited = image in user.favorite_images

        if is_collected:
            user.collect_images.remove(image)
        if is_favorited:
            user.favorite_images.remove(image)

        # 提交移除收藏和喜欢操作
        if is_collected or is_favorited:
            db.session.commit()

        # 删除关联表中所有关于该图片的记录
        db.session.execute(user_collect_images.delete().where(user_collect_images.c.image_id == image_id))
        db.session.execute(user_favorite_images.delete().where(user_favorite_images.c.image_id == image_id))

        # 删除图片本身
        db.session.delete(image)
        db.session.commit()

        return jsonify({'message': '图片已删除', 'code': 200}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



#                                     管理后台接口

# 下架壁纸
# 修改is_off_shelf 字段为False 即可
# @wallpaper_bp.route('/admin/images/off_shelf', methods=['POST'])
# def off_shelf_image():
#        image_id = request.form.get('image_id')
#        print(image_id)
#        try:
#            image = Image.query.get(image_id)
#            if image is None:
#                return jsonify({'error': '图片不存在'}), 404
#
#            image.is_off_shelf = 0
#            db.session.commit()
#
#            return jsonify({'message': '图片已下架', 'code': 200}), 200
#
#        except Exception as e:
#            db.session.rollback()
#
# # 重新上架壁纸
# @wallpaper_bp.route('/admin/images/<int:image_id>/on_shelf', methods=['PUT'])
# def on_shelf_image(image_id):
#     try:
#         image = Image.query.get(image_id)
#         if image is None:
#             return jsonify({'error': '图片不存在'}), 404
#
#         image.is_off_shelf = 1
#         db.session.commit()
#
#         return jsonify({'message': '图片已经重新上架', 'code': 200}), 200
#
#     except Exception as e:
#         db.session.rollback()
#
# # 获取所有下架的壁纸
# @wallpaper_bp.route('/admin/images/getAll_off_shelf', methods=['GET'])
# def get_off_shelf_images():
#     try:
#         images = Image.query.filter_by(is_off_shelf=True).all()
#         image_list = [image.to_dict() for image in images]
#
#         return jsonify({'images': image_list}), 200
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500