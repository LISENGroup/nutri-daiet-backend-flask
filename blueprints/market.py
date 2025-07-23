# market.py
# 市场相关

from flask_jwt_extended import jwt_required,get_jwt_identity

from models import CartItem,Product,OrderItem,Order,ProductViewHistory,Merchant,Promotion,FavoriteMerchant,Invoice,FavoriteProduct,Review

from datetime import datetime
import random

from flask import request, jsonify,Blueprint,make_response
from exts import db

# 创建令牌
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt
)



# 市场蓝图
bp=Blueprint("market",__name__,url_prefix="/api/market")




# 商家入驻
# 商家邮箱注册
@bp.route('/merchant/captcha_register', methods=['POST'])
def merchant_captcha_register():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'message': '缺少必要参数'}), 400
    
    if Merchant.query.filter_by(email=data['email']).first() is not None:
        return jsonify({'message': '邮箱已被注册'}), 400
    
    new_merchant = Merchant(
        name=data.get('name', ''),
        headshot_url=data.get('headshot_url',''),
        address=data.get('address', ''),
        phone_number=data.get('phone_number', ''),
        email=data['email']
    )
    new_merchant.set_password(data['password'])  
    
    db.session.add(new_merchant)
    db.session.commit()
    
    return jsonify({'message': '商家注册成功'}), 201


# 商家登录
@bp.route('/login_with_email', methods=['POST'])
def login_with_email():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'message': '缺少必要参数'}), 400
    
    merchant = Merchant.query.filter_by(email=data['email']).first()
    product_list=Product.query.filter_by(merchant_id=merchant.id).all()
    if merchant is None or not merchant.check_password(data['password']):
        return jsonify({'message': '无效的邮箱或密码'}), 401
    access_token = create_access_token(identity=merchant.id)
    response=make_response({
        'code':200,
        'success':True,
        'message':'成功登录',
        'access_token': access_token,
        'merchant': {
            'id':merchant.id,
            'name':merchant.name,
            'headshot_url':merchant.headshot_url,
            'address':merchant.address,
            'phone_number':merchant.phone_number,
            'email':merchant.email,
            'product_list':product_list

        }
            
        })

    return response




from werkzeug.security import generate_password_hash
# 商家修改密码
@bp.route('/merchant_change_password',methods=['POST'])
@jwt_required()
def merchant_change_password():
    merchant_id=get_jwt_identity()
    merchant=Merchant.query.filter_by(id=merchant_id).first()
    data=request.get_json()
    password=data.get('password')
    
    password_hash=generate_password_hash(password)
   
    if password_hash:
        merchant.password_hash=password_hash
        db.session.commit()
        return jsonify({'message': f'用户的密码修改成功'}), 200
    else:
        return jsonify({'message': f'用户未填写密码'}), 400



# 商家创建商品
@bp.route('/create_product', methods=['POST'])
@jwt_required()  
def create_product():
    data = request.get_json()
    merchant_id=get_jwt_identity()
    if not data or not 'name' in data or not 'price' in data:
        return jsonify({
            'code': 400,
            'message': '缺少必要参数'
        }), 400
    
    name = data['name']
    price = data['price']
    imageurl=data['imageurl']
    description = data.get('description', '') 
    stock=data.get('stock')
    refund=data.get('refund')
    return_policy=data.get('return_policy')
    compensation=data.get('compensation')
    
    new_product = Product(
        merchant_id=merchant_id,
        name=name, 
        price=price, 
        description=description,
        imageurl=imageurl,
        stock=stock,
        refund=refund,
        return_policy=return_policy,
        compensation=compensation
        )
    
    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify({
            'code': 201,
            'data': {
                'id': new_product.id,
                'merchant_id':merchant_id,
                'name': new_product.name,
                'price': new_product.price,
                'description': new_product.description,
                'imageurl':imageurl,
                'stock':stock,
                'refund':refund,
                'return_policy':return_policy,
                'compensation':compensation
            },
            'message': '商品创建成功'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'error': str(e)
        }), 500



# 商家更新商品信息
@bp.route('/product/<int:product_id>/update', methods=['PUT'])
@jwt_required()  
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    if 'name' in data: product.name = data['name']
    if 'price' in data: product.price = data['price']
    if 'description' in data: product.description = data['description']
    if 'stock' in data: product.stock = data['stock']
    if 'imageurl' in data: product.imageurl = data['imageurl']
    if 'refund' in data: product.refund = data['refund']
    if 'return_policy' in data: product.return_policy = data['return_policy']
    if 'compensation' in data: product.compensation = data['compensation']
    
    db.session.commit()
    return jsonify({'code': 200, 'message': '商品更新成功'})


# 商家查看自己的商品
@bp.route('/merchant_product', methods=['GET'])
@jwt_required() 
def get_merchant_products():
    merchant_id=get_jwt_identity()
    merchant_products = Product.query.filter_by(merchant_id=merchant_id)
    return jsonify({
        'code': 200, 
        'data': [{  
                'id': p.id,
                'merchant_id':p.merchant_id,
                'name': p.name,
                'price': p.price,
                'description': p.description,
                'imageurl':p.imageurl,
                'stock':p.stock,
                'refund':p.refund,
                'return_policy':p.return_policy,
                'compensation':p.compensation
        } for p in merchant_products]  
    })

# 查看所有商品
@bp.route('/product', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify({
        'code': 200,  
        'data': [{  
                'id': p.id,
                'merchant_id':p.merchant_id,
                'name': p.name,
                'price': p.price,
                'description': p.description,
                'imageurl':p.imageurl,
                'stock':p.stock,
                'refund':p.refund,
                'return_policy':p.return_policy,
                'compensation':p.compensation
        } for p in products]  
    })




# 从全部商品中搜索
@bp.route('product_search',methods=['POST'])
def product_search():
    data=request.get_json()
    search_query = data.get('key')

    products=Product.query.filter(Product.name.contains(search_query)
        | Product.description.contains(search_query)
                                  ).all()

# 查看某个商品（在查看商品的时候记录浏览历史）
@bp.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'code': 200, 
        'data': {    
            'id': product.id,           
            'name': product.name,      
            'price': product.price,     
            'description': product.description,  
            'imageurl':product.imageurl
        }
    })

# 购物车
@bp.route('/shop_cart', methods=['POST'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cartitems = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cartitems:
        return jsonify({'code': 400, 'message': '购物车中没有商品'})
    
    return jsonify({
        'code': 200,
        'data': [{
            'product_id': item.product_id,
            'user_id':item.user_id,
            'quantity': item.quantity,
            'name':Product.query.filter_by(id=item.product_id).first().name,
            'price':Product.query.filter_by(id=item.product_id).first().price,
            'imageurl':Product.query.filter_by(id=item.product_id).first().imageurl,
            'refund':Product.query.filter_by(id=item.product_id).first().refund,
            'return_policy':Product.query.filter_by(id=item.product_id).first().return_policy,
            'compensation':Product.query.filter_by(id=item.product_id).first().compensation,
            'merchant_id':Product.query.filter_by(id=item.product_id).first().merchant_id,
            'merchant_name':Merchant.query.filter_by(id=Product.query.filter_by(id=item.product_id).first().merchant_id).first().name,
            'merchant_headshot_url':Merchant.query.filter_by(id=Product.query.filter_by(id=item.product_id).first().merchant_id).first().headshot_url

            
        } for item in cartitems] 
    })


# 添加商品到购物车
@bp.route('/shop_cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product = Product.query.get_or_404(data['product_id'])
    cart_item = CartItem.query.filter_by(
        user_id=user_id,
        product_id=data['product_id']
    ).first()
    if cart_item:
        cart_item.quantity += data.get('quantity', 1)
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=data['product_id'],
            quantity=data.get('quantity', 1)
        )
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify({'code': 200, 'message': '商品被添加到购物车'})





# 修改购物车中单个商品的数量，如果为0便将商品从购物车中删除
@bp.route('/shop_cart/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(product_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    quantity = data.get('quantity', 1)

    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first_or_404()

    if quantity <= 0:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'code': 200, 'message': f'商品{product_id}已从购物车中移除'}), 200
    else:
        cart_item.quantity = quantity
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': f'购物车中的商品数量更新为{quantity}',
            'data': {
                'product_id': cart_item.product_id,
                'quantity': cart_item.quantity
            }
        }), 200



# 生成订单号
def generate_order_number():
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"

# 账单
@bp.route('/order', methods=['POST'])
@jwt_required()
def order():
    user_id = get_jwt_identity()
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({'code': 400, 'message': '购物车是空的'}), 400
    order_number = generate_order_number()
    total = sum(item.quantity * Product.query.filter_by(id=item.product_id).first().price for item in cart_items)
    new_order = Order(
        user_id=user_id,
        order_number=order_number,
        total_amount=total
    )
    
    db.session.add(new_order)
    db.session.commit()
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=Product.query.filter_by(id=item.product_id).first().price
        )
        db.session.add(order_item)
    CartItem.query.filter_by(user_id=user_id).delete()

    db.session.commit()
    return jsonify({
        'code': 201,
        'data': {
            'order_number': order_number,
            'total': total
        }
    }), 201







# 商家信息更新
@bp.route('/update_merchant_info', methods=['POST'])
@jwt_required()
def update_merchant_info():
    merchant_id = get_jwt_identity()
    data = request.get_json()

    merchant = Merchant.query.get_or_404(merchant_id)
    merchant.contact_info = data.get('contact_info', merchant.contact_info)
    merchant.open_hours = data.get('open_hours', merchant.open_hours)
    merchant.announcement = data.get('announcement', merchant.announcement)

    db.session.commit()
    return jsonify({'message': '商家信息更新成功'}), 200



# 查看商家详情
@bp.route('/merchant/<int:merchant_id>', methods=['GET'])
def get_merchant_details(merchant_id):
    merchant = Merchant.query.get_or_404(merchant_id)
    # 返回商家详细信息
    details = {
        'address': merchant.address,
        'contact_info': merchant.contact_info,
        'open_hours': merchant.open_hours,
        'announcement': merchant.announcement,
        'ratings': merchant.ratings if hasattr(merchant, 'ratings') else None  # 假设有一个字段存储评价
    }
    return jsonify(details), 200



# 商家登出
@bp.route('/merchant_logout', methods=['POST'])
@jwt_required()
def merchant_logout():
    jti = get_jwt()['jti']
    # 可以在此处将jti加入黑名单以实现token失效
    return jsonify({'message': '商家已登出'}), 200



# 商家删除商品
@bp.route('/delete_product/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    merchant_id = get_jwt_identity()
    product = Product.query.filter_by(id=product_id, merchant_id=merchant_id).first_or_404()
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': '商品删除成功'}), 200



# 更新库存状态
@bp.route('/update_inventory/<int:product_id>', methods=['POST'])
@jwt_required()
def update_inventory(product_id):
    merchant_id = get_jwt_identity()
    inventory_status = request.get_json().get('stock_status')
    product = Product.query.filter_by(id=product_id, merchant_id=merchant_id).first_or_404()
    product.stock_status = inventory_status
    db.session.commit()
    return jsonify({'message': '库存状态更新成功'}), 200


# 商品分类浏览
@bp.route('/products_by_category/<string:category>', methods=['GET'])
def products_by_category(category):
    products = Product.query.filter_by(category=category).all()
    return jsonify([p.to_dict() for p in products]), 200


# 商品推荐（基于用户的浏览历史进行推荐）
@bp.route('/recommend_products/<int:user_id>', methods=['GET'])
def recommend_products(user_id):
    viewed_products = ProductViewHistory.query.filter_by(user_id=user_id).all()
    viewed_product_ids = [pv.product_id for pv in viewed_products]
    recommended_products = Product.query.filter(Product.id.notin_(viewed_product_ids)).limit(5).all()
    return jsonify([p.to_dict() for p in recommended_products]), 200


# 从购物车中移除商品
@bp.route('/remove_from_cart/<int:cart_item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_item_id):
    user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(id=cart_item_id, user_id=user_id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': '商品已从购物车移除'}), 200


# 清空购物车
@bp.route('/clear_cart', methods=['POST'])
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'message': '购物车已清空'}), 200



# 生成订单
@bp.route('/create_order', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    # 根据用户的购物车创建订单逻辑...
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total_amount = sum(Product.query.get(item.product_id).price * item.quantity for item in cart_items)
    order_number = generate_order_number()
    
    new_order = Order(
        user_id=user_id,
        order_number=order_number,
        total_amount=total_amount
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=Product.query.get(item.product_id).price
        )
        db.session.add(order_item)
    
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'message': '订单创建成功'}), 200


# 查看订单状态
@bp.route('/order_status/<int:order_id>', methods=['GET'])
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = {'status': order.status}
    return jsonify(status), 200


# 取消订单
@bp.route('/cancel_order/<int:order_id>', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'pending':
        return jsonify({'message': '无法取消此订单'}), 400
    order.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': '订单已取消'}), 200


# 评价商品
@bp.route('/review_product/<int:product_id>', methods=['POST'])
@jwt_required()
def review_product(product_id):
    user_id = get_jwt_identity()
    rating = request.get_json().get('rating')
    comment = request.get_json().get('comment')
    # 创建评价逻辑...
    review = Review(user_id=user_id, product_id=product_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': '评价提交成功'}), 200


# 收藏商品/商家
@bp.route('/toggle_favorite/<string:type>/<int:id>', methods=['POST'])
@jwt_required()
def toggle_favorite(type, id):
    user_id = get_jwt_identity()
    if type == 'product':
        favorite = FavoriteProduct.query.filter_by(user_id=user_id, product_id=id).first()
        if favorite:
            db.session.delete(favorite)
        else:
            new_favorite = FavoriteProduct(user_id=user_id, product_id=id)
            db.session.add(new_favorite)
    elif type == 'business':
        favorite = FavoriteMerchant.query.filter_by(user_id=user_id, business_id=id).first()
        if favorite:
            db.session.delete(favorite)
        else:
            new_favorite = FavoriteMerchant(user_id=user_id, business_id=id)
            db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'message': f'{type}收藏切换成功'}), 200


# 促销活动
@bp.route('/promotions', methods=['GET'])
def promotions():
    now = datetime.now()
    promotions = Promotion.query.filter(Promotion.start_date <= now, Promotion.end_date >= now).all()
    return jsonify([promo.to_dict() for promo in promotions]), 200


# 生成唯一的发票号码
import time
def generate_invoice_number():
    """
    生成唯一的发票号码。
    此处使用时间戳结合随机数的方式来确保唯一性。
    """
    timestamp = int(time.time() * 1000)  
    random_part = random.randint(1000, 9999) 
    return f'INV-{timestamp}-{random_part}'

# 商家生成发票
@bp.route('/create_invoice/<int:order_id>', methods=['POST'])
@jwt_required()
def create_invoice(order_id):
    data = request.get_json()
    merchant_id = get_jwt_identity()  
    
    order = Order.query.filter_by(id=order_id, user_id=merchant_id).first_or_404()
    invoice_number = generate_invoice_number() 
    
    new_invoice = Invoice(
        order_id=order.id,
        merchant_id=merchant_id,
        invoice_number=invoice_number,
        amount=order.total_amount,
        type=data.get('type', '普通发票')
    )
    
    db.session.add(new_invoice)
    db.session.commit()
    return jsonify({'message': '发票创建成功'}), 201