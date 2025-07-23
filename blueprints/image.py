
import Food_Rec
from flask import (
    Blueprint,request,jsonify
)
from PIL import Image
import io


from flask import Blueprint, request, jsonify
import Food_Rec

# 返回图像识别的结果
bp = Blueprint("image", __name__, url_prefix="/image")

@bp.route("/res", methods=['POST'])
def login():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        try:
            img = Image.open(io.BytesIO(file.read()))
            result = Food_Rec.food_recognition(img)
            
            return jsonify({
                'result': result
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file format'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
