# 数据库的配置信息
hostname = '127.0.0.1'
port = "3306"
database = 'ff_minimalist_wallpapers'
username = 'root'
password = '123456'

DB_URL = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(username, password, hostname, port, database)

SQLALCHEMY_DATABASE_URI = DB_URL
 
""" import secrets

# 生成一个随机的密钥
jwt_secret_key = secrets.token_hex(32)  # 生成64位的十六进制密钥
print(jwt_secret_key) """