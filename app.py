# Flask网站框架


from flask import (
    Flask,jsonify,request
)
import config
from exts import db,mail,login_manager,limiter,jwt
from flask_migrate import Migrate
from blueprints import (
    ai,auth,user,community,market,image,message
)
from flask_cors import CORS


# 设置保存文件的路径
import os
UPLOAD_FOLDER = './static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# flask实例
app = Flask(__name__)

# 各种扩展
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(config)
db.init_app(app)
mail.init_app(app)
jwt.init_app(app)
migrate=Migrate(app,db)
login_manager.init_app(app)
limiter.init_app(app)

# 蓝图
app.register_blueprint(ai.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)
app.register_blueprint(community.bp)
app.register_blueprint(market.bp)
app.register_blueprint(image.bp)
app.register_blueprint(message.bp)

CORS(app) 

# 全局错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '找不到资源，404'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器错误，500'}), 500
    


@app.route("/")
def hello():
     return """
        这里是主页,啥也没有 <br>
        <a href="about">about</a><br>
        """

@app.route('/about')
def about():
    return '这里是后端服务器,需要前端调用接口'

import uuid

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "请求中没有文件部分"}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        # 返回文件访问地址
        file_url = f"/static/uploads/{unique_filename}"
        return jsonify({"message": "文件上传成功", "file_url": file_url}), 200
    
    return jsonify({"error": "文件类型不允许"}), 400

if __name__ == '__main__':
    app.run()


    
