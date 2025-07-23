# config.py
# 各种配置信息

# 数据库的配置信息
HOSTNAME='127.0.0.1'
PORT='3306'
DATABASE='web_2025'
USERNAME='root'
PASSWORD='123456'
DB_URI='mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)
SQLALCHEMY_DATABASE_URI=DB_URI


# 邮箱配置
MAIL_SERVER="smtp.qq.com"
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME="官方邮箱"
MAIL_PASSWORD="官方邮箱发送验证码所需的密码"
MAIL_DEFAULT_SENDER="官方邮箱"



# 配置密钥
JWT_SECRET_KEY="kajkf12@di&a"
from datetime import timedelta
JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=7)  
