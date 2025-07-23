# auth.py
# 账号相关

from flask import Blueprint,request,jsonify,make_response
from models import User,EmailCaptcha
from exts import db,mail
from flask_mail import Message
import string
import random
from datetime import datetime
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity
)

# 账号蓝图
bp=Blueprint("auth",__name__,url_prefix="/api/auth")



# 获取邮箱验证码路由
@bp.route("/captcha/email",methods=['POST'])
def get_email_captcha():
    email=request.get_json().get("email")
    if is_valid_email(email):
        return jsonify({'message':f"{email} 不是有效的邮箱地址"})
    if  User.query.filter_by(email=email).first() is not None:
        return jsonify({'message': '邮箱已被注册'}), 409
    
    source=string.digits*6
    captcha=random.sample(source,4)
    captcha="".join(captcha)
    message=Message(subject="网站注册验证码",recipients=[email],body=f"您的验证码是：{captcha}")
    mail.send(message)
    email_captcha=EmailCaptcha(email=email,captcha=captcha)
    db.session.add(email_captcha)
    db.session.commit()
    return jsonify({"code":200,"message":"验证码获取成功","data":captcha})


# 账号注册
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('captcha'):
        return jsonify({'message': '没有邮箱或密码或验证码'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': '邮箱已被注册'}), 409    
    
    captcha = data['captcha']
    email = data['email']
    if is_valid_email(email):
        return jsonify({'message':f"{email} 不是有效的邮箱地址"})
    captcha_model = EmailCaptcha.query.filter_by(email=email, captcha=captcha).first()
    if not captcha_model:
        return jsonify({'message': '邮箱或验证码错误'}), 401
    else:
        db.session.delete(captcha_model)
        db.session.commit()


    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'message': '账号创建成功', 
        'user': user.to_dict()  
    }), 201


# 账号登录
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email=data['email']
    if is_valid_email(email):
        return jsonify({'message':f"{email} 不是有效的邮箱地址"})
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': '找不到用户或者密码验证失败'}), 401
    if not user.is_active:
        return jsonify({'message': '用户账户被标记为非激活状态'}), 403
    

    access_token = create_access_token(identity=user.id)
    user.last_login = datetime.now()
    db.session.commit()
    response=make_response({
        'code':200,
        'success':True,
        'message':'成功登录',
        'access_token': access_token,
        'user': user.to_dict()  
        })
    response.set_cookie('email',email,max_age=60*60*24*30)
    return response







# 手机号注册，登录

# 账号注册
@bp.route('/register_with_phone', methods=['POST'])
def register_with_phone():
    data = request.get_json()
    if not data or not data.get('phone_number') or not data.get('password'):
        return jsonify({'message': '用户没有填写手机号或密码'}), 400
    if User.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'message': '手机号已被注册'}), 409    
    phone_number = data['phone_number']
    pattern = r"^1[3-9]\d{9}$"
    import re
    if not re.match(pattern, phone_number):
        return jsonify({'message': '手机号格式不对'}), 400
    
    user = User(phone_number=data['phone_number'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': '账号创建成功', 
        'user': user.to_dict() 
    }), 201



# 账号登录
@bp.route('/login_with_phone', methods=['POST'])
def login_with_phone():
    data = request.get_json()
    phone_number=data['phone_number']
    user = User.query.filter_by(phone_number=data.get('phone_number')).first()
    if not user :
        return jsonify({'message': '找不到用户或者密码验证失败'}), 401
    if not user.is_active:
        return jsonify({'message': '用户账户被标记为非激活状态'}), 403
    
    access_token = create_access_token(identity=user.id)
    user.last_login = datetime.now()
    db.session.commit()
    response=make_response({
        'code':200,
        'success':True,
        'message':'成功登录',
        'access_token': access_token,
        'user': user.to_dict() 
        })
    response.set_cookie('phone_number',phone_number,max_age=60*60*24*30)
    return response



# 绑定手机号
@bp.route('/set_phone',methods=['POST'])
@jwt_required()
def set_phone():
    user_id=get_jwt_identity()
    # 返回对应id的用户信息
    user=User.query.filter_by(id=user_id).first()
    phone_number=request.get_json().get('phone_number')
    if phone_number:
        user.phone_number=phone_number
        # 提交更改到数据库，保存更新的信息
        db.session.commit()
        return jsonify({'message': f'用户绑定手机号为{phone_number}'}), 200
    else:
        return jsonify({'message': '用户未填写手机号'}), 400
    




# 绑定邮箱
@bp.route('/set_email',methods=['POST'])
@jwt_required()
def set_email():
    user_id=get_jwt_identity()
    # 返回对应id的用户信息
    user=User.query.filter_by(id=user_id).first()
    email=request.get_json().get('email')
    if is_valid_email(email):
        return jsonify({'message':f"{email} 不是有效的邮箱地址"})
    if email is not None:
        user.email=email
        # 提交更改到数据库，保存更新的信息
        db.session.commit()
        return jsonify({'message': f'用户绑定邮箱为{email}'}), 200
    else:
        return jsonify({'message': '用户未填写邮箱'}), 400
    

import re
# 验证邮箱格式
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is None


from werkzeug.security import generate_password_hash
# 修改密码
@bp.route('/change_password',methods=['POST'])
@jwt_required()
def change_password():
    user_id=get_jwt_identity()
    user=User.query.filter_by(id=user_id).first()
    data=request.get_json()
    password=data.get('password')
    
    password_hash=generate_password_hash(password)
   
    if password_hash:
        user.password_hash=password_hash
        db.session.commit()
        return jsonify({'message': f'用户的密码修改成功'}), 200
    else:
        return jsonify({'message': f'用户未填写密码'}), 400



# 账号登出
@bp.route('/logout', methods=['POST'])
@jwt_required() 
def logout():
    jti = get_jwt()['jti']
    return jsonify({'message': '成功退出账号'}), 200



import pyotp
# 安全设置
@bp.route('/settings/2fa', methods=['POST'])
@jwt_required()
def toggle_2fa():
    user_id = get_jwt_identity()
    action = request.get_json().get('action') 
    user = User.query.filter_by(id=user_id).first()

    if action == 'enable':
        if not user.otp_secret:
            user.otp_secret = pyotp.random_base32()
        return jsonify({
            'message': '2FA 已启用', 
            'otp_uri': pyotp.totp.TOTP(user.otp_secret).provisioning_uri(name=user.email, issuer_name="膳食app")
            }), 200
    elif action == 'disable':
        user.otp_secret = None
        db.session.commit()
        return jsonify({'message': '2FA 已禁用'}), 200
    else:
        return jsonify({'message': '无效操作'}), 400
    


# 封禁账号
from datetime import *


@bp.route('/admin/ban_user', methods=['POST'])
def ban_user():
    user_id = request.get_json().get('user_id')
    duration = request.get_json().get('duration')  
    reason = request.get_json().get('reason')
    user = User.query.filter_by(id=user_id).first()

    if user:
        user.is_banned = True
        user.ban_end_date = datetime.now() + timedelta(days=duration)
        user.ban_reason = reason
        db.session.commit()
        return jsonify({'message': f'用户 {user.email} 已被封禁'}), 200
    else:
        return jsonify({'message': '用户不存在'}), 404


@bp.route('/admin/unban_user', methods=['POST'])
def unban_user():
    user_id = request.get_json().get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if user and user.is_banned:
        user.is_banned = False
        user.ban_end_date = None
        user.ban_reason = None
        db.session.commit()
        return jsonify({'message': f'用户 {user.email} 的封禁已被解除'}), 200
    else:
        return jsonify({'message': '用户未被封禁或不存在'}), 404