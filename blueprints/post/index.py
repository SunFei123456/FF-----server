

#  导入日期
from datetime import datetime

from flask import Blueprint, json, jsonify, request
from flask_jwt_extended import jwt_required

from model.index import Post_Comment, Post_Topic, Post_like, Post, Post_like

post_bp = Blueprint('post', __name__, url_prefix='/post')

# 1. 用户发表帖子

@post_bp.route('/create', methods=['POST'])
@jwt_required()
def create_post():
    content = request.json.get('content')
    user_id = request.json.get('user_id')
    images = request.json.get('images')
    created_at = datetime.now()
    if content is None:
        return jsonify({'message': '内容不能为空', 'code': 400}), 400
    # 创建帖子
    post = Post.create(user_id=user_id, content=content, images=images,created_at=created_at)
    return jsonify({'message': '帖子创建成功', 'code': 200, 'post_id': post.id}), 201

# 2. 用户删除帖子
@post_bp.route('/delete/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({'message': '帖子不存在', 'code': 404}), 404
    Post.delete(post_id)
    return jsonify({'message': '帖子删除成功', 'code': 200}), 200

# 3. 用户点赞or 取消点赞帖子
@post_bp.route('/like_or_cancelLike', methods=['PUT'])
def like_or_cancelLike_post():
    post_id = request.json.get('post_id')
    user_id = request.json.get('user_id')
    like =Post_like.query.filter_by(user_id=user_id, post_id=post_id).first()
    # is none then create like record
    if like is None:
        Post_like.create(user_id=user_id, post_id=post_id)
        return jsonify({'message': '点赞成功', 'code': 200}), 200
    else:
    # not none then delete like record
        Post_like.delete(like_id=like.id)
        return jsonify({'message': '取消点赞成功', 'code': 200}), 200


# 5. 获取所有帖子
@post_bp.route('/all', methods=['GET'])
def get_all_post():
    posts = Post.getAll()
    return jsonify({'code': 200, 'data': posts,'message': '获取成功'}), 200


# 6. 增加帖子浏览量
@post_bp.route('/view/<int:post_id>', methods=['PUT'])
def view_post(post_id):
    Post.add_view(post_id)
    return jsonify({'message': '浏览量增加成功', 'code': 200}), 200

# 7. 评论帖子
@post_bp.route('/comment', methods=['POST'])
def comment_post():
    user_id = request.json.get('user_id')
    post_id = request.json.get('post_id')
    content = request.json.get('content')
    parent_id = request.json.get('parent_id')
    
    if content is None:
        return jsonify({'message': '评论内容不能为空', 'code': 400}), 400
    
    comment = Post_Comment.create(user_id=user_id, post_id=post_id, content=content,parent_id=parent_id)
    if comment:
        return jsonify({'message': '评论成功', 'code': 200, 'comment_id': comment.id}), 201
    else:
        return jsonify({'message': '评论失败', 'code': 500}), 500

# 8. 删除评论
@post_bp.route('/comment/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        result = Post_Comment.delete(comment_id)
        if result:
            return jsonify({'message': '评论删除成功', 'code': 200}), 200
    except Exception as e:
        return jsonify({'message': '删除评论时出错', 'code': 500, 'error': str(e)}), 500


# 9. 获取帖子的评论
@post_bp.route('/comment/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    comments = Post_Comment.getComments(post_id)
    comments_data = [comment.to_dict() for comment in comments]
    return jsonify({'message': '获取评论成功', 'code': 200, 'data': comments_data}), 200


# 10. 获取指定话题下的所有帖子
@post_bp.route('/topic/<int:topic_id>', methods=['GET'])
def get_topic_posts(topic_id):
    posts = Post.getTopicPosts(topic_id)
    posts_data = [post.to_dict() for post in posts]
    return jsonify({'message': '获取帖子成功', 'code': 200, 'data': posts_data}), 200
    