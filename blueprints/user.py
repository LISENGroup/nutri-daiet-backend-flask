# user.py
# 用户相关

from flask import Blueprint,jsonify,request,send_file

from models import User,UserTag

from exts import db



# 用户蓝图
bp=Blueprint("user",__name__,url_prefix="/api/user")



# 用户个人资料
@bp.route('/profile/<user_id>',methods=['GET'])
def profile(user_id):
    # 返回对应id的用户信息
    user=User.query.filter_by(id=user_id).first()
    usertags=UserTag.query.filter_by(user_id=user_id).all()
    tag_list=[usertag.tag for usertag in usertags]
    if user:
        return jsonify({
            'id': user.id,
            'username':user.username,
            'age':user.age,
            'headshot_url':user.headshot_url,
            'signature':user.signature,
            'email': user.email,
            'phone_number':user.phone_number,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'follow_num':user.follow_num,
            'fan_num':user.fan_num,
            'like_favorite_num':user.like_favorite_num,
            "usertags":tag_list
        })
    else:
        return jsonify({'message': '找不到该用户'}), 404
    


import qrcode
import io
# 创建个人二维码
@bp.route('/qr/<path:url>')
def generate_qr(url):

    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# 修改用户名
@bp.route('/username/<user_id>',methods=['POST'])
def username(user_id):
    user=User.query.filter_by(id=user_id).first()
    username=request.get_json().get('username')
    if username:
        user.username=username
        db.session.commit()
        return jsonify({'message': '用户名修改成功'}), 200
    else:
        return jsonify({'message': '用户未填写用户名'}), 400
    

# 修改年龄
@bp.route('/age/<user_id>',methods=['POST'])
def age(user_id):
    user=User.query.filter_by(id=user_id).first()
    age=request.get_json().get('age')
    if age:
        user.age=age
        db.session.commit()
        return jsonify({'message': f'用户修改年龄为{age}岁'}), 200
    else:
        return jsonify({'message': '用户未填写年龄'}), 400
    
# 修改头像
@bp.route('/headshot/<user_id>',methods=['POST'])
def headshot_url(user_id):
    user=User.query.filter_by(id=user_id).first()
    headshot_url=request.get_json().get('headshot_url')
    if headshot_url:
        user.headshot_url=headshot_url
        db.session.commit()
        return jsonify({'message': f'用户头像的地址为{headshot_url}'}), 200
    else:
        return jsonify({'message': '用户未上传头像'}), 400
    
# 修改个性签名
@bp.route('/signature/<user_id>',methods=['POST'])
def signature(user_id):
    user=User.query.filter_by(id=user_id).first()
    signature=request.get_json().get('signature')
    if signature:
        user.signature=signature
        db.session.commit()
        return jsonify({'message': f'用户的个性签名修改为{signature}'}), 200
    else:
        return jsonify({'message': '用户未填写个性签名'}), 400
    





# 添加用户标签
@bp.route('/addtag/<user_id>',methods=['POST'])
def addtag(user_id):
    usertag=request.get_json().get('usertag')
    if not usertag:
        return jsonify({'message': '用户未填写标签内容'}), 400
    else:
        tag=UserTag(tag=usertag,user_id=user_id)
        db.session.add(tag)
        db.session.commit()

        return jsonify({
            'message':'标签添加成功',
            'tag':tag.to_dict()
        })
    
# 删除用户标签
@bp.route('/reducetag/<tag_id>',methods=['POST'])
def reducetag(tag_id):
    tag=UserTag.query.filter_by(id=tag_id).first()
    if not tag:
        return jsonify({'message': '该标签不存在'}), 400
    else:
        db.session.delete(tag)
        db.session.commit()
        return jsonify({
            'message':'标签删除成功'
        })

#展示某用户所有标签
@bp.route('/taglist/<user_id>',methods=['POST'])
def taglist(user_id):
   
    tags=UserTag.query.filter_by(user_id=user_id).all()
    if not tags:
        return jsonify({'message': '该用户没有标签'}), 400
    else:
        # 将标签转换为字典列表
        tags_list = [tag.to_dict() for tag in tags]
        return jsonify({
            'message':'用户所有标签',
            'tags':tags_list
        })

