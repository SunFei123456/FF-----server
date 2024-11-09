# #  编写关于question的路由(蓝图)
#
# # 导入Flask类
# from flask import Blueprint, abort, jsonify
#
# # 导入模型
# from models.question.index import Question
#
# # 定义蓝图
# question_bp = Blueprint('question', __name__, url_prefix='/question')
#
#
# # 编写路由, 返回问题列表
# @question_bp.route('/getAll', methods=['GET'])
# def get_all_questions():
# 	try:
# 		questions = Question.query.all()
# 	except Exception as e:
# 		abort(500, description="服务器错误")
#
# 	if not questions:
# 		abort(404, description="没有找到相关资源")
#
# 	question_list = [{
# 		'id': question.id,
# 		'title': question.title,
# 		'content': question.content
# 	} for question in questions]
#
# 	return jsonify({
# 		"data": question_list,
# 		"message": "获取成功"
# 	}), 200
#
#
# @question_bp.errorhandler(404)
# def not_found_error(error):
# 	#  定义 404 错误的响应
# 	return jsonify({'error': 'Not found', 'message': error.description}), 404
