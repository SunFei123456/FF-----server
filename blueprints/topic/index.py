import os

from flask import Blueprint, jsonify, request
from model.index import Post_Topic, Topic


# 定义蓝图
topic_bp = Blueprint('topic', __name__, url_prefix='/topics')


# 1. 获取所有话题
@topic_bp.route('', methods=['GET'])
def get_all_topics():
    topics = Topic.getAll()
    # 计算话题参与人数 也就是该话题下的帖子数量 可以在Post_topic表中查找
    for topic in topics:
        topic.join_nums = Post_Topic.getTopicPostsCount(topic.id)
    # 序列化话题数据
    if topics:
        topics_list = [{'id': topic.id, 'name': topic.name, 'description': topic.description, 'views': topic.view_count, 'joins': topic.join_nums} for topic in topics]
        return {'code': 200, 'msg': '获取成功', 'data': topics_list}
    else:
        return {'code': 404, 'msg': '话题不存在'}
    
# 2. 创建一个话题
@topic_bp.route('/create', methods=['POST'])
def create_topic():
    name = request.json.get('name')
    description = request.json.get('description')
    if name is None:
        return jsonify({'message': '话题名称不能为空', 'code': 400}), 400
    # 如果name已经存在，返回错误信息
    if Topic.getByName(name):
        return jsonify({'message': '话题名称已存在', 'code': 400}), 400
    new_topic = Topic.create(name=name, description=description)
    return jsonify({'message': '话题创建成功', 'code': 200, 'data': new_topic.id}), 200, 


# 3. bind 一个话题到一个帖子
@topic_bp.route('/bind', methods=['POST'])
def bind_topic_to_post():
    post_id = request.json.get('post_id')
    topic_id = request.json.get('topic_id')
    if post_id is None or topic_id is None:
        return jsonify({'message': 'post_id 和 topic_id 不能为空', 'code': 400}), 400
    Post_Topic.create(post_id, topic_id)
    return jsonify({'message': '话题绑定成功', 'code': 200}), 200

# 4. 获取浏览量较高的话题
@topic_bp.route('/hot', methods=['GET'])
def get_hot_topics():
    topics = Topic.getHotTopics()
    # 序列化话题数据
    if topics:
        topics_list = [{'id': topic.id, 'name': topic.name, 'description': topic.description, 'views': topic.view_count} for topic in topics]
        return {'code': 200,'msg': '获取成功', 'data': topics_list}, 200
    else:
        return {'code': 404,'msg': '话题不存在'}, 404
    

# 5. 获取话题下的帖子
@topic_bp.route('/<int:topic_id>/posts', methods=['GET'])
def get_topic_posts(topic_id):
    posts = Post_Topic.getTopicPosts(topic_id)
    return jsonify({'message': '获取帖子成功', 'code': 200, 'data': posts}), 200

# 6. 根据话题id获取话题信息
@topic_bp.route('/<int:topic_id>', methods=['GET'])
def get_topic_by_id(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    return jsonify({'message': '获取话题成功', 'code': 200, 'data': topic.to_dict()}), 200