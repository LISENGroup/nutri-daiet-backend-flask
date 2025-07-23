# models.py
# 各种模型

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from exts import db


# 账号，用户板块

# 验证码模型
class EmailCaptcha(db.Model):
    # 验证码表
    __tablename__="email_captchas"
    # 验证码id
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    # 邮箱
    email=db.Column(db.String(100),nullable=False)
    # 验证码
    captcha=db.Column(db.String(100),nullable=False)
    

# 关注关联表
followers=db.Table('followers',
                    db.Column('follower_id',db.Integer,db.ForeignKey('users.id')),
                    db.Column('followed_id',db.Integer,db.ForeignKey('users.id'))
                    )

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    otp_secret = db.Column(db.String(16), nullable=True)  
    is_banned = db.Column(db.Boolean, default=False)
    ban_end_date = db.Column(db.DateTime, nullable=True)
    ban_reason = db.Column(db.String(256), nullable=True)
    username = db.Column(db.String(64), default='username',nullable=True)
    age=db.Column(db.Integer,nullable=True)
    headshot_url=db.Column(db.String(256),nullable=True)
    signature=db.Column(db.String(256),nullable=True)
    follow_num=db.Column(db.Integer,default=0,nullable=False)
    fan_num=db.Column(db.Integer,default=0,nullable=False)
    like_favorite_num=db.Column(db.Integer,default=0,nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=True)
    phone_number = db.Column(db.String(15), unique=True, index=True, nullable=True)  
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    tags = db.relationship('UserTag', backref='user', lazy='dynamic')
    following=db.relationship('User',
                              secondary='followers',
                              primaryjoin=(id==followers.c.follower_id),
                              secondaryjoin=(id==followers.c.followed_id),
                                backref=db.backref('followers', lazy='dynamic'), 
                                lazy='dynamic')



    def follow(self, user):
            if not self.is_following(user):
                self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username':self.username,
            'age':self.age,
            'headshot_url':self.headshot_url,
            'signature':self.signature,
            'email': self.email,
            'phone_number':self.phone_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'follow_num':self.follow_num,
            'fan_num':self.fan_num,
            'like_favorite_num':self.like_favorite_num
        }
    

# 用户标签模型
class UserTag(db.Model):
    __tablename__ = 'user_tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'user_id': self.user_id
        }




# 社区板块

# 基础模型类
class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)



class Post(BaseModel):
    __tablename__='posts'
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'title':self.title,
            'content':self.content,
            'created_at':self.created_at,
            'updated_at':self.updated_at
        }

class Comment(BaseModel):
    __tablename__='comments'
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    
    def to_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'post_id':self.post_id,
            'content':self.content,
            'created_at':self.created_at,
            'updated_at':self.updated_at
        }

# 点赞模型
class Like(BaseModel):
    __tablename__='likes'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    def to_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'post_id':self.post_id,
            'created_at':self.created_at,
            'updated_at':self.updated_at
        }

# 收藏模型
class Favorite(BaseModel):
    __tablename__='favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    def to_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'post_id':self.post_id,
            'created_at':self.created_at,
            'updated_at':self.updated_at
        }





# 市场模块

# 商品-标签关联表
product_tag_association = db.Table('product_tag_association',
                                   db.Column('product_id', db.Integer, db.ForeignKey('products.id')),
                                   db.Column('tag_id', db.Integer, db.ForeignKey('product_tags.id'))
                                   )

# 商品
class Product(BaseModel):
    __tablename__='products'
    id = db.Column(db.Integer, primary_key=True)
    merchant_id=db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    imageurl=db.Column(db.String(256))
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    refund = db.Column(db.Boolean, default=False)  
    return_policy = db.Column(db.Boolean, default=False)
    compensation = db.Column(db.Boolean, default=False) 
    stock_status = db.Column(db.String(10), default='in_stock')  
    tags = db.relationship('ProductTag', secondary=product_tag_association, backref='products')



# 商品评价
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False) 
    rating = db.Column(db.Float, nullable=False)  
    comment = db.Column(db.Text)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    user = db.relationship('User', backref='reviews')
    product = db.relationship('Product', backref='reviews')

class Product(BaseModel):
    stock_status = db.Column(db.String(10), default='in_stock')  # 新增字段


# 商品标签模型
class ProductTag(db.Model):
    __tablename__ = 'product_tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# 收藏商品
class FavoriteProduct(db.Model):
    __tablename__ = 'favorite_products'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())



# 购物车
class CartItem(BaseModel):
    __tablename__='cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=db.func.now())


# 订单目录
class OrderItem(db.Model):
    __tablename__='order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# 订单具体信息
class Order(db.Model):
    __tablename__='orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.now())


# 商家
class Merchant(BaseModel):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    headshot_url=db.Column(db.String(256),nullable=True)
    address = db.Column(db.String(256))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# 收藏商家
class FavoriteMerchant(db.Model):
    __tablename__ = 'favorite_merchants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

# 促销活动
class Promotion(db.Model):
    __tablename__ = 'promotions'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

# 商品浏览记录
class ProductViewHistory(BaseModel):
    __tablename__ = 'product_view_histories'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    viewed_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'viewed_at': self.viewed_at,
        }
    
# 商家的发票
class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # 关联订单
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 发票开具商家
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)  # 发票号码
    amount = db.Column(db.Float, nullable=False)  # 发票金额
    created_at = db.Column(db.DateTime, default=db.func.now())  # 发票创建时间
    status = db.Column(db.String(20), default='pending')  # 发票状态（例如：待审核、已开具、已取消）
    type = db.Column(db.String(20), nullable=False)  # 发票类型（例如：普通发票、增值税专用发票）

    order = db.relationship('Order', backref='invoice')

# 问答模块
class Question(db.Model):
    __tablename__='questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref=db.backref('questions', lazy=True))

class Answer(db.Model):
    __tablename__='answers'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref=db.backref('answers', lazy=True))
    question = db.relationship('Question', backref=db.backref('answers', lazy=True))



# 伪聊天模块

class Message(db.Model):
    __tablename__='messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')



# 浏览记录
class ViewHistory(BaseModel):
    __tablename__ = 'view_histories'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    viewed_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'viewed_at': self.viewed_at,
        }
    
