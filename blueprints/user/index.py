import os
from datetime import datetime

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, jwt_required

from extensions import db

# 导入model

from model.index import Post, User, Image, user_favorite_images, user_followers

# 定义蓝图
user_bp = Blueprint('user', __name__, url_prefix='/user')


# 注册
@user_bp.route('/register', methods=['POST'])
def register():
	# 获取注册的表单信息
	data = request.json
	userName = data.get('reg_username')
	email = data.get('reg_email')
	password = data.get('reg_password')
	print(userName, email, password)

	# 检查必填字段
	if not userName or not email or not password:
		return jsonify({'error': '缺少必要字段'}), 400

	# 检查邮箱是否已经被注册了
	existing_user = User.query.filter_by(email=email).first()
	if existing_user:
		return jsonify({'error': '该邮箱已被注册'}), 400

	# 加密密码
	hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)


	# 将用户信息保存到数据库（这里只是示例，在实际项目中应保存到数据库）
	# 记录当前用户的注册时间
	time = datetime.now()
	User.create(userName=userName, email=email, password=hashed_password, create_time=time)

	# 生成token
	access_token = create_access_token(identity=email)
	return jsonify({'message': '注册成功', 'code': 200,'access_token': access_token}), 201


# 登录
@user_bp.route('/login', methods=['POST'])
def login():
    # 获取登录的表单信息
    data = request.json
    email = data.get('email')
    password = data.get('password')

    print(email, password)
    # 检查必填字段
    if not email or not password:
        return jsonify({'error': '完整输入'}), 400

    # 从数据库获取用户信息
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 计算用户的图片数量和帖子数量
    images_count = Image.query.filter_by(create_by=user.id).count()
    posts_count = Post.query.filter_by(user_id=user.id).count()

	# 打印
    print("213123123131", images_count, posts_count)
    # 验证密码
    if not check_password_hash(user.password, password):
        return jsonify({'error': '密码有误'}), 401

    

    # 生成 token
    access_token = create_access_token(identity=email)

    # 获取用户信息
    data = {
        'user_id': user.id,
        'user_name': user.username,
        'email': user.email,
        'create_time': user.create_time,
        'nickname': user.nickname,
        'gender': user.gender,
        'birth': user.birth,
        'country': user.country,
        'province': user.province,
        'city': user.city,
        'image': user.image,
        'description': user.description,
        'like_count': user.like_count,
        'followers_count': user.followers_count,
        'favorite_count': user.favorite_count,
        'follow_count': user.follow_count,
        'person_home_background_image': user.person_home_background_image,
        'images_count': images_count,
        'posts_count': posts_count,
    }
    return jsonify({'message': '登录成功', 'data': data, 'code': 200, 'access_token': access_token}), 200

# 用户头像上传
UPLOAD_FOLDER = 'static'


@user_bp.route('/upload_avatar', methods=['POST'])
def upload_avatar():
	# 获取上传的文件
	file = request.files.get('avatar')
	print(file)
	if not file:
		return jsonify({'error': '没有上传文件'}), 400
	filename = secure_filename(file.filename)  # 拿到上传图片的名字
	# 保存文件
	file_path = os.path.join(UPLOAD_FOLDER, filename)  # 拿到上传图片的路径
	file.save(file_path)
	image_url = f'http://127.0.0.1:5000/{file_path}'

	return jsonify({'message': '头像上传成功', 'code': 200, 'image_url': image_url}), 200


# 绑定用户头像
@user_bp.route('/bind_avatar', methods=['POST'])
def bind_avatar():
	user_id = request.json.get('user_id')
	image_url = request.json.get('image_url')

	# 更新数据库
	user = User.query.get(user_id)
	user.image = image_url
	db.session.commit()
	db.session.close()

	return jsonify({'message': '头像绑定成功', 'code': 200, 'image_url': image_url}), 200


# 用户信息修改
# http://localhost:5000/user/update_userInfo
@user_bp.route('/update_userInfo', methods=['POST'])
def update_userInfo():
	user_id = request.json.get('user_id')
	nickname = request.json.get('nickname')
	gender = request.json.get('gender')
	birth = request.json.get('birth')
	# country
	country = request.json.get('country')
	# province
	province = request.json.get('province')
	# city
	city = request.json.get('city')
	# description
	description = request.json.get('description')

	# 将其解析为 datetime 对象
	birth_datetime = datetime.fromisoformat(birth.rstrip('Z'))

	# 将 datetime 对象转换为 MySQL 支持的日期字符串格式（仅日期部分）
	birth_mysql_format = birth_datetime.strftime('%Y-%m-%d')

	# 更新数据库
	user = User.query.get(user_id)
	user.nickname = nickname
	user.gender = gender
	user.birth = birth_mysql_format
	user.country = country
	user.province = province
	user.city = city
	user.description = description
	db.session.commit()
	db.session.close()

	return jsonify({'message': '用户信息更新成功', 'code': 200}), 200


# 获取用户上传的图片列表
@user_bp.route('/get_user_images', methods=['GET'])
def get_user_images():
	# 获取用户的id
	user_id = request.args.get('user_id')
	# 通过id在Image表中查找
	images = Image.query.filter_by(create_by=user_id).all()
	# 将查找的图片的进行返回
	if images:
		image_list = []
		for image in images:
			create_time = image.create_time.strftime('%Y-%m-%d %H:%M:%S')
			image_list.append({
				'image_id': image.id,
				'image_url': image.url,
				'image_description': image.alt,
				'image_upload_time': create_time
			})
		return jsonify({'data': image_list, 'code': 200}), 200
	else:
		return jsonify({'message': '该用户没有上传图片', 'code': 200}), 200


# 定义了两个路由 /user/<int:user_id>/likes 和 /user/<int:user_id>/collects。
# get_user_likes 函数查询并返回指定用户喜欢的图片。
# get_user_collects 函数查询并返回指定用户收藏的图片。
# 如果用户不存在，返回 404 错误和相应的错误信息。

@user_bp.route('/<int:user_id>/likes', methods=['GET'])
def get_user_likes(user_id):
	user = User.query.get_or_404(user_id)
	likes = user.favorite_images
	like_images = []
	for like in likes:
		like_images.append({
			'image_id': like.id,
			'image_url': like.url,
			'image_description': like.alt,
			'image_upload_time': like.create_time.strftime('%Y-%m-%d %H:%M:%S')
		})
	return jsonify({'data': like_images, 'code': 200}), 200


@user_bp.route('/<int:user_id>/collects', methods=['GET'])
def get_user_collects(user_id):
	user = User.query.get_or_404(user_id)
	collects = user.collect_images
	collects_images = []
	for item in collects:
		collects_images.append({
			'image_id': item.id,
			'image_url': item.url,
			'image_description': item.alt,
			'image_upload_time': item.create_time.strftime('%Y-%m-%d %H:%M:%S')
		})
	return jsonify({'data': collects_images, 'code': 200}), 200


# 根据用户id 获取用户的信息
@user_bp.route('/info/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
	user = User.query.get_or_404(user_id)
	# 获取用户喜欢的图片数量
	like_count = len(user.favorite_images)
	# 获取用户收藏的图片数量
	collect_count = len(user.collect_images)
	# 获取用户发帖的数量
	post_count =  Post.query.filter_by(user_id=user_id).count()
	# 获取用户上传的壁纸数量
	wallpapers = Image.query.filter_by(create_by=user_id).count()
 
	userInfo = {
		'user_id': user.id,
		'user_email': user.email,
		'user_nickname': user.nickname,
		'user_avatar': user.image,
		'follow_count': user.follow_count,
		'followers_count': user.followers_count,
		'posts' : post_count,
		'wallpapers': wallpapers,
		'user_like_count': like_count,
		'user_collect_count': collect_count,
		'user_country': user.country,
		'user_province': user.province,
		'user_city': user.city,
		'user_description': user.description,
		'person_home_background_image': user.person_home_background_image
	}
	return jsonify({"code":200, "data":userInfo,"message": "获取成功"}), 200


# 喜欢or取消喜欢 壁纸
@user_bp.route('/toggleLikeImage', methods=['POST'])
@jwt_required()
def toggle_like_image():
    user_id = request.json.get('user_id')
    image_id = request.json.get('image_id')
    user = User.query.get_or_404(user_id)
    image = Image.query.get_or_404(image_id)

    # 检查当前用户是否已经喜欢过该壁纸
    if image in user.favorite_images:
        # 如果已经喜欢，则取消喜欢
        user.favorite_images.remove(image)
        image.like_count -= 1
        creator = User.query.get_or_404(image.create_by)
        creator.like_count -= 1
        message = '取消喜欢成功'
    else:
        # 如果没有喜欢，则添加喜欢
        user.favorite_images.append(image)
        image.like_count += 1
        creator = User.query.get_or_404(image.create_by)
        creator.like_count += 1
        message = '喜欢成功'

    db.session.commit()

    return jsonify({'code': 200, 'message': message}), 200



@user_bp.route('/toggleCollectImage', methods=['POST'])
@jwt_required()
def toggle_collect_image():
    user_id = request.json.get('user_id')
    image_id = request.json.get('image_id')
    user = User.query.get_or_404(user_id)
    image = Image.query.get_or_404(image_id)
    # 检查当前用户是否已经收藏过该壁纸
    if image in user.collect_images:
        # 如果已经收藏，则取消收藏
        user.collect_images.remove(image)
        image.favorite_count -= 1
        message = '取消收藏成功'
    else:
        # 如果没有收藏，则添加收藏
        user.collect_images.append(image)
        image.favorite_count += 1
        message = '收藏成功'
        
    db.session.commit()

    return jsonify({'code': 200, 'message': message}), 200



# 用户下载作品,  接收用户的id. 以及作品的id
@user_bp.route('/downloadImage', methods=['POST'])
@jwt_required()
def download_image():
    image_id = request.json.get('image_id')
    
    try:
        # 拿到当前的图片信息
        image = Image.query.get_or_404(image_id)
        
        # 增加当前的图片的下载数
        image.download_count += 1
        db.session.commit()  # 提交更改
        
        # 返回图片的 URL
        return jsonify({'code': 200, 'data': image.url, 'message': '下载成功'}), 200
        
    except Exception as e:
        db.session.rollback()  # 如果出错，回滚事务
        return jsonify({'code': 500, 'message': str(e)}), 500
    finally:
        db.session.close()  # 确保会话在结束时关闭


# 用户关注行为操作
@user_bp.route('/followUser', methods=['POST'])
def follow_user():
	follower_id = request.json.get('follower_id')  # 当前用户id
	followed_id = request.json.get('followed_id')  # 被关注用户id

	print(follower_id, followed_id)

	if not follower_id or not followed_id:
		return jsonify({'message': 'Follower ID and Followed ID are required.'}), 400

	follower = User.query.get(follower_id)
	followed = User.query.get(followed_id)

	if not follower or not followed:
		return jsonify({'message': '用户找不到.'}), 404

	# 判断是否已经关注
	if follower.following.filter(user_followers.c.followed_id == followed_id).count() > 0:
		return jsonify({'message': '已经关注了该作者.'}), 400

	try:
		# 插入中间表
		follower.following.append(followed)

		# 更新用户的关注数和粉丝数
		follower.follow_count += 1
		followed.followers_count += 1

		# 提交事务
		db.session.commit()

		return jsonify({'message': '成功关注.', 'code': 200}), 200
	except Exception as e:
		db.session.rollback()
		return jsonify({'message': str(e)}), 500


# 用户取消关注行为操作
@user_bp.route('/unfollowUser', methods=['POST'])
def unfollow_user():
	follower_id = request.json.get('follower_id')  # 当前用户id
	followed_id = request.json.get('followed_id')  # 被取消关注的用户id

	if not follower_id or not followed_id:
		return jsonify({'message': 'Follower ID and Followed ID are required.'}), 400

	follower = User.query.get(follower_id)
	followed = User.query.get(followed_id)

	if not follower or not followed:
		return jsonify({'message': '用户找不到.'}), 404

	# 判断是否已经关注
	if follower.following.filter(user_followers.c.followed_id == followed_id).count() == 0:
		return jsonify({'message': '未关注该用户.'}), 400

	try:
		# 从中间表中移除记录
		follower.following.remove(followed)

		# 更新用户的关注数和粉丝数
		follower.follow_count -= 1
		followed.followers_count -= 1

		# 提交事务
		db.session.commit()

		return jsonify({'message': '取消关注成功.', 'code': 200}), 200
	except Exception as e:
		db.session.rollback()
		return jsonify({'message': str(e)}), 500


# 获取用户的粉丝和关注数
@user_bp.route('/getFollowCount/<int:user_id>', methods=['GET'])
def get_user_follows(user_id):
	user = User.query.get(user_id)

	if not user:
		return jsonify({'message': 'User not found.'}), 404

	followers_count = user.followers.count()
	following_count = user.following.count()

	return jsonify({
		'followers_count': followers_count,
		'following_count': following_count
	}), 200


# 用来返回一个bool值, 标识当前用户是否关注了另外一个用户
@user_bp.route('/<int:user_id>/is_following/<int:author_id>', methods=['GET'])
def is_following(user_id, author_id):
	user = User.query.get(user_id)
	author = User.query.get(author_id)
	print(11)
	print(user, author)
	if not user or not author:
		return jsonify({'message': 'User not found.'}), 404

	# 判断当前用户是否已经关注了该作者
	is_following = user.following.filter(user_followers.c.followed_id == author_id).count() > 0

	return jsonify({'is_following': is_following}), 200


# 修改个人中心页资料模块的后方背景
# 接收图片url , 和 user_id.
# 讲user_id 对应的user数据的 person_home_background_image 的值 指定为 接收图片url
# 修改个人中心页资料模块的后方背景
@user_bp.route('/modify_background', methods=['POST'])
def modify_background():
	data = request.get_json()
	user_id = data.get('user_id')
	background_image_url = data.get('background_image_url')

	if not background_image_url:
		return jsonify({'message': '图片 URL 是必须的'}), 400

	user = User.query.get(user_id)

	if not user:
		return jsonify({'message': '用户未找到'}), 404

	try:
		user.person_home_background_image = background_image_url
		db.session.commit()
		return jsonify({'message': '背景图片更新成功', 'code': 200}), 200
	except Exception as e:
		db.session.rollback()
		return jsonify({'message': str(e)}), 500



# 获取发帖数量前三的用户
@user_bp.route('/get_top_users', methods=['GET'])
def get_top_users():
    # 获取发帖数量前三的用户及其发帖数量
    top_users = (
        db.session.query(User, func.count(Post.id).label('post_count'))  # 获取用户和发帖数量
        .join(Post)  # 连接 User 和 Post 表
        .group_by(User.id)  # 按用户 ID 分组
        .order_by(func.count(Post.id).desc())  # 按发帖数量降序排列
        .limit(3)  # 限制结果为前3个用户
        .all()
    )

    # 构建返回数据
    result = [{'user': user.to_dict(), 'post_count': post_count} for user, post_count in top_users]

    return jsonify({'code': 200, 'message': '获取成功', 'data': result}), 200




#                                  admin - apis


# 获取所有的用户 (没有被冻结的用户)
@user_bp.route('/get_all_users', methods=['GET'])
def get_all_users():
	# 修正 SQLAlchemy 查询语句中的布尔逻辑
	users = User.query.filter(User.role == 'user').all()
	result = []

	if users:
		# 去除不需要的字段并创建字典
		for user in users:
			# 处理时间格式
			create_time = user.create_time.strftime('%Y-%m-%d %H:%M:%S')
			user_data = {
				'id': user.id,
				'username': user.username,
				'email': user.email,
				'gender': user.gender,
				'address': f'{user.country,  user.province , user.city}',
				'create_time': create_time,
				'status': user.status,
				'role': user.role,

			}
			result.append(user_data)

		return jsonify({'users': result}), 200
	else:
		return jsonify({'message': 'not found'}), 404

# 获取所有管理员
@user_bp.route('/get_all_administrators', methods=['GET'])
def get_all_administrators():
	users = User.query.filter( User.role == 'admin').all()
	result = []

	if users:
		# 去除不需要的字段并创建字典
		for user in users:
			# 处理时间格式
			create_time = user.create_time.strftime('%Y-%m-%d %H:%M:%S')
			user_data = {
				'id': user.id,
				'username': user.username,
				'email': user.email,
				'gender': user.gender,
				'address': f'{user.country,  user.province , user.city}',
				'create_time': create_time,
				'status': user.status,
				'role': user.role,

			}
			result.append(user_data)

		return jsonify({'users': result}), 200
	else:
		return jsonify({'message': 'not found'}), 404
