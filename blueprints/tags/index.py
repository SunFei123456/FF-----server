# 导入模型
from flask import Blueprint

from model.index import Tag

# 定义一个蓝图
tag_bp = Blueprint('tag', __name__,url_prefix='/tag')



# 获取所有标签
@tag_bp.route('/get_all_tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    if tags:
        tags_list = [{'id': tag.id, 'name': tag.name} for tag in tags]
        return {'code': 200, 'msg': '获取成功', 'data': tags_list}
    else:
        return {'code': 404, 'msg': '标签不存在'}



