from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from exts import db
from models import User,Message

# 消息蓝图
bp = Blueprint('message', __name__,url_prefix="/api/message")


@bp.route('/send_message/<receiver_id>', methods=['POST'])
@jwt_required()
def send_message(receiver_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    content = data.get('content')

    if not receiver_id or not content:
        return jsonify({"message": "缺少接收者id或消息内容"}), 400

    receiver = User.query.filter_by(id=receiver_id).first_or_404()
    sender= User.query.filter_by(id=current_user_id).first_or_404()
    message = Message(sender_id=current_user_id, receiver_id=receiver.id, content=content)
    db.session.add(message)
    db.session.commit()

    return jsonify({"message": f"{sender.username}向{receiver.username}发送：{content}"}), 201


# 显示（对面发给我的和我发给对面的）全部消息
@bp.route('/get_messages/<receiver_id>', methods=['GET'])
@jwt_required()
def get_messages( receiver_id):
    current_user_id = get_jwt_identity()

    receiver = User.query.filter_by(id=receiver_id).first_or_404()

    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == receiver.id)) |
        ((Message.sender_id == receiver.id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.timestamp.asc()).all()

    return jsonify([{
        "sender": msg.sender.username,
        "receiver": msg.receiver.username,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat()
    } for msg in messages])