from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy.orm import joinedload

from extensions import db

# 中间表，用于壁纸和标签的多对多关系
image_tags = db.Table('image_tags',
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# 中间表, 用于用户和喜欢的作品的多对多关系
user_favorite_images = db.Table('user_favorite_images',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True)
)

# 中间表, 用于用户和收藏的作品的多对多关系
user_collect_images = db.Table('user_collect_images',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True)
)

# 中间表，用于用户和关注的用户的多对多关系
user_followers = db.Table('user_followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    alt = db.Column(db.String(255))
    type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # 将 size 拆分为 file_size 和 dimensions
    dimensions = db.Column(db.String(50), nullable=False)
    create_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    download_count = db.Column(db.Integer, default=0, nullable=True)
    like_count = db.Column(db.Integer, default=0, nullable=True)
    favorite_count = db.Column(db.Integer, default=0, nullable=True)
    # 壁纸的状态 审核中 or 审核通过, 默认审核中
    status = db.Column(db.String(50), default='审核中', nullable=True)
    # 0 false 1 ture

    # 关系字段，用于获取图片的标签
    tags = db.relationship('Tag', secondary=image_tags, lazy='subquery',
        backref=db.backref('images', lazy=True))



class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # 存储加密后的密码
    email = db.Column(db.String(255), nullable=False, unique=True)
    nickname = db.Column(db.String(100))
    gender = db.Column(db.Enum('male', 'female', 'other'), nullable=True,default='other')
    birth = db.Column(db.Date, nullable=True)
    country = db.Column(db.String(100), nullable=True,default='中国')
    province = db.Column(db.String(100), nullable=True,default='广东')
    city = db.Column(db.String(100), nullable=True,default='广州')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_time = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.Enum('user', 'admin'), default='user', nullable=True)
    status = db.Column(db.Enum('active', 'inactive', 'banned'), default='active', nullable=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    followers_count = db.Column(db.Integer, default=0, nullable=True)
    like_count = db.Column(db.Integer, default=0, nullable=True)
    favorite_count = db.Column(db.Integer, default=0, nullable=True)
    follow_count = db.Column(db.Integer, default=0, nullable=True)

    # 2024/5/24 add 字段, 个人中心页面的上方背景
    person_home_background_image = db.Column(db.String(255), nullable=True)

    # 关系字段, 用于获取用户喜欢的图片
    favorite_images = db.relationship('Image', secondary=user_favorite_images, backref=db.backref('favorited_by_users',
                                                                                                  lazy='dynamic'))
    # 关系字段, 用于获取用户收藏的图片
    collect_images = db.relationship('Image', secondary=user_collect_images, backref=db.backref('collected_by_users',
                                                                                                lazy='dynamic'))
    # 关系字段, 用于获取用户关注的用户和粉丝
    following = db.relationship('User', secondary=user_followers,
                                primaryjoin=(user_followers.c.follower_id == id),
                                secondaryjoin=(user_followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'),
                                lazy='dynamic')
 
    
    def to_dict(self):
        return {
            'id': self.id,
            'image': self.image,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname,
    }
    @classmethod
    def create(cls, userName, email, password,create_time):
            new_user = cls(username=userName, email=email, password=password,create_time=create_time)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        
    




# 帖子表
class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, index=True)

    user = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
    
    @classmethod
    def create(cls, user_id, content, images, created_at):
        new_post = cls(user_id=user_id, content=content, images=images, created_at=created_at)
        db.session.add(new_post)
        db.session.commit()
        return new_post
    
  
    
    @classmethod
    def delete(cls, post_id):
        # 删除帖子的评论
        Post_Comment.delete_comments(post_id)

        # 删除帖子的点赞
        Post_like.query.filter_by(post_id=post_id).delete()
        # 删除帖子绑定的话题,如果存在的话
        Post_Topic.query.filter_by(post_id=post_id).delete()
        # 删除帖子
        db.session.delete(cls.query.get_or_404(post_id))
        db.session.commit()
        return True
    
    @classmethod
    def getAll(cls):
        # 使用 joinedload 来预加载用户信息
        posts = (
            cls.query
            .options(joinedload(cls.user)) 
            .order_by(cls.created_at.desc())
            .all()
        )

        # 获取每个帖子的点赞数量和评论数据
        post_likes = {post.id: [like.to_dict() for like in db.session.query(Post_like).filter_by(post_id=post.id).all()] for post in posts}
        post_comments = {post.id: [comment.to_dict() for comment in db.session.query(Post_Comment).filter_by(post_id=post.id).all()] for post in posts}
        
        # 获取每个帖子的bind的话题
        post_topics = {post.id: [topic.to_dict() for topic in db.session.query(Post_Topic).filter_by(post_id=post.id).all()] for post in posts}
        return [
            post.to_dict_with_user_and_likes(post_likes.get(post.id, []), post_comments.get(post.id, []), post_topics.get(post.id, {})) for post in posts
        ]

    @classmethod
    # 增加帖子浏览量
    def add_view(cls, post_id):
        post = cls.query.get_or_404(post_id)
        post.views += 1
        db.session.commit()
        return post
     
    # 方法：将模型转换为字典，包含用户信息和点赞数据和评论
    def to_dict_with_user_and_likes(self, likes, comments, topics):
        # 从likes获取所有点赞的用户信息
        likes_with_user = []
        for like in likes:
            user = User.query.get(like['user_id'])
            if user:
                likes_with_user.append({
                    'id': like['id'],
                    'user_id': like['user_id'],
                    'post_id': like['post_id'],
                    'created_at': like['created_at'],
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'image':user.image,
                        'email': user.email
                    }
                })
        
        # 话题
        

        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'images': self.images,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'description':self.user.description,
                'image':self.user.image,
                'email': self.user.email
                # 其他用户信息
            },
            'likes': likes_with_user,
            'comments': comments,
            'created_at':self.created_at.isoformat(),
            'topics': topics,
        }
        
    
# 帖子点赞表
class Post_like(db.Model):
    __tablename__ = 'post_like'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Add a to_dict method
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }
    

    @classmethod
    def create(cls, user_id, post_id):
        new_favor = cls(user_id=user_id, post_id=post_id)
        db.session.add(new_favor)
        db.session.commit()
        return new_favor
    
    @classmethod
    def delete(cls, like_id):
        favor = cls.query.get_or_404(like_id)
        db.session.delete(favor)
        db.session.commit()
        return True


# 帖子评论表
class Post_Comment(db.Model):
    __tablename__ = 'post_comment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comment.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 多对一的关系
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))
    
    # 自引用关系，用于父子评论
    parent_comment = db.relationship('Post_Comment', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))

    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'image': self.user.image
            },
            'replies': [reply.to_dict() for reply in self.replies]
        }
        
    @classmethod
    def create(cls, user_id, post_id, content, parent_id):
        try:
            data = cls(user_id=user_id, post_id=post_id, content=content, parent_id=parent_id)
            db.session.add(data)
            db.session.commit()
            return data
        except Exception as e:
            db.session.rollback()
            print("Error:", e)
            return None
        
    @classmethod

    def delete(cls, comment_id):
        comment = cls.query.get_or_404(comment_id)
        
        # 递归删除所有子评论
        def recursive_delete(cmt):
            for reply in cmt.replies:
                recursive_delete(reply)
            db.session.delete(cmt)
        
        recursive_delete(comment)
        db.session.commit()
        return True

    @classmethod
    def delete_comments(cls, post_id):
        comments = Post_Comment.query.filter_by(post_id=post_id).all()
        for comment in comments:
            if comment.replies:
                cls.delete_comments(comment.id)
            db.session.delete(comment)
        db.session.commit()
        
        
    # get comments of 指定的post
    @classmethod 
    def getComments(cls, post_id):
        comments = cls.query.filter_by(post_id=post_id).all()
        # 根据 parent_id  获取 子评论
        for comment in comments:
            comment.replies = cls.query.filter_by(parent_id=comment.id).all()
        
        return comments
 
      
            
# 话题表
class Topic(db.Model):
    __tablename__ = 'topic'
    
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  
    description = db.Column(db.Text, nullable=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'view_count': self.view_count
        }
    @classmethod
    def getAll(cls):    
        return cls.query.all()
    
    @classmethod
    def create(cls, name, description):
        new_topic = cls(name=name, description=description)
        db.session.add(new_topic)
        db.session.commit()
        return new_topic
    
    @classmethod
    def getByName(cls, name):
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def getHotTopics(cls):
        topics = cls.query.order_by(cls.view_count.desc()).limit(3).all()
        return topics
    
    


# 话题中间表, 帖子 和 话题 post_id 和 topic_id
class Post_Topic(db.Model):
    __tablename__ = 'post_topic'
    
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), primary_key=True, nullable=False)
    
    # 定义一个方法,根据topic_id 从 topic table 拿到name
    @property
    def topic_name(self):
        topic = Topic.query.get(self.topic_id)
        return topic.name

    def to_dict(self):
        return {
            "post_id": self.post_id,
            "topic_id": self.topic_id,
            "topic_name": self.topic_name
        }
    # 参与话题
    @classmethod
    def create(cls, post_id, topic_id):
        new_topic = cls(post_id=post_id, topic_id=topic_id)
        db.session.add(new_topic)
        db.session.commit()
        return new_topic
    
    # 获取指定话题下的帖子数量
    @classmethod
    def getTopicPostsCount(cls, topic_id):
        return cls.query.filter_by(topic_id=topic_id).count()
    
    # 获取指定话题下的所有帖子
    @classmethod
    def getTopicPosts(cls, topic_id):
        # 查询指定话题下的所有帖子
        posts = (
            db.session.query(Post)
            .join(cls)
            .filter(cls.topic_id == topic_id)
            .options(joinedload(Post.user))  # 预加载用户信息
            .order_by(Post.created_at.desc())
            .all()
        )     
         # 获取每个帖子的点赞数量和评论数据
        post_likes = {post.id: [like.to_dict() for like in db.session.query(Post_like).filter_by(post_id=post.id).all()] for post in posts}
        post_comments = {post.id: [comment.to_dict() for comment in db.session.query(Post_Comment).filter_by(post_id=post.id).all()] for post in posts}
        
        # 获取每个帖子的bind的话题
        post_topics = {post.id: [topic.to_dict() for topic in db.session.query(Post_Topic).filter_by(post_id=post.id).all()] for post in posts}
        
        return [
            post.to_dict_with_user_and_likes(post_likes.get(post.id, []), post_comments.get(post.id, []), post_topics.get(post.id, {})) for post in posts
        ]
        
        
