# community.py
# 社区相关


from flask import Blueprint,request, jsonify
from models import Post, Comment, Like,User,Question,Answer,Favorite,ViewHistory
from exts import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# 社区蓝图
bp=Blueprint("community",__name__,url_prefix="/api/community")



# 创建文章
@bp.route('/posts', methods=['POST'])
@jwt_required()  
def create_post():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_post = Post(title=data['title'],content=data['content'], user_id=user_id)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({
        'message': '文章创建成功', 
        'new_post': new_post.to_dict() 
    }), 201


# 查看某一篇文章（在查看文章的时候记录浏览历史）
@bp.route('/posts/<int:post_id>', methods=['POST'])
@jwt_required()
def get_post(post_id):
    user_id=get_jwt_identity()
    post = Post.query.get_or_404(post_id, description="文章不存在")
    view_history = ViewHistory(user_id=user_id, post_id=post_id)
    db.session.add(view_history)
    db.session.commit()
    return jsonify(post.to_dict()), 200

# 查看历史记录
@bp.route('/post_view_history', methods=['POST'])
@jwt_required()
def get_view_history():
    user_id = get_jwt_identity()
    histories = ViewHistory.query.filter_by(user_id=user_id).order_by(ViewHistory.viewed_at.desc()).all()
    
    posts = []
    for history in histories:
        post = Post.query.get(history.post_id)
        if post:
            posts.append(post.to_dict())
    
    return jsonify({
        'view_history': posts,
    }), 200    

# 搜索历史记录
@bp.route('/post_view_history/search', methods=['POST'])
@jwt_required()
def search_view_history():
    user_id = get_jwt_identity()
    
    
    histories = ViewHistory.query.filter_by(user_id=user_id).all()
    post_ids = [historie.post_id for historie in histories]
    data=request.get_json()
    search_query = data.get('key')


    liked_posts = Post.query.filter(Post.id.in_(post_ids))\
        .filter(Post.title.contains(search_query) | Post.content.contains(search_query))\
        .all()
    
    histories_posts_dicts = [post.to_dict() for post in liked_posts]
    return jsonify({
        'histories_search_results': histories_posts_dicts,
    }), 200



# 清空历史记录
@bp.route('/history/clear', methods=['DELETE'])
@jwt_required()
def clear_view_history():
    user_id = get_jwt_identity()
    ViewHistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"msg": "历史记录已清空"}), 200



# 删除某个历史记录
@bp.route('/history/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_view_history(post_id):
    user_id = get_jwt_identity()
    view_history_to_delete = ViewHistory.query.filter_by(user_id=user_id, post_id=post_id).first()
    if view_history_to_delete is None:
        return jsonify({"msg": "未找到对应的历史记录"}), 404
    
    db.session.delete(view_history_to_delete)
    db.session.commit()
    
    return jsonify({"msg": "历史记录删除成功"}), 200


# 查看数据库全部文章
@bp.route('/posts/list', methods=['POST'])
def get_posts():
    all_posts = Post.query.all()
    posts_list = [post.to_dict() for post in all_posts]
    return jsonify(posts_list), 200



# 查看某用户的全部文章
@bp.route('/users/<int:user_id>/list', methods=['POST'])
def get_user_posts(user_id):
    user_posts = Post.query.filter_by(user_id=user_id).all()
    
    if not user_posts:
        return jsonify({"msg": "该用户没有文章"}), 404
    
    posts_list = [post.to_dict() for post in user_posts]
    return jsonify(posts_list), 200



# 从某用户的全部文章中搜索
@bp.route('/users/<int:user_id>/list_search', methods=['POST'])
def get_user_posts_search(user_id):
    data=request.get_json()
    search_query = data.get('key')
    user_posts = Post.query.filter_by(user_id=user_id)\
        .filter(Post.title.contains(search_query) | Post.content.contains(search_query))\
        .all()
    
    if not user_posts:
        return jsonify({"msg": "搜索不到相应文章"}), 404
    
    posts_dicts = [post.to_dict() for post in user_posts]
    return jsonify({
        'user_posts_search_results':posts_dicts
    }), 200



# 写评论
@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()  
def add_comment(post_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_comment = Comment(content=data['content'], 
                         user_id=user_id,
                         post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(new_comment.to_dict()), 201



# 查看某个文章的全部评论
@bp.route('/posts/<int:post_id>/comments', methods=['GET','POST'])
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    
    if not comments:
        return jsonify({"msg": "该文章没有任何评论"}), 404
    comments_list = [comment.to_dict() for comment in comments]
    return jsonify(comments_list), 200
    


# 添加点赞功能
@bp.route('/posts/<int:post_id>/likes', methods=['POST'])
@jwt_required() 
def add_like(post_id):
    user_id = get_jwt_identity()
    if Like.query.filter_by(user_id=user_id, post_id=post_id).first() is not None:
        return jsonify({"msg": "用户已经点赞了该文章"}), 400
    new_like = Like(user_id=user_id, post_id=post_id)
    db.session.add(new_like)
    db.session.commit()
    return jsonify(new_like.to_dict()), 201


# 取消点赞功能
@bp.route('/posts/<int:post_id>/likes', methods=['DELETE'])
@jwt_required()  
def remove_like(post_id):
    user_id = get_jwt_identity()
    like_to_remove = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if like_to_remove is None:
        return jsonify({"msg": "没有点赞过"}), 404
    db.session.delete(like_to_remove)
    db.session.commit()
    return jsonify({"msg": "成功取消点赞"}), 200




# 收藏模块

# 添加收藏功能
@bp.route('/posts/<int:post_id>/add_favorite', methods=['POST'])
@jwt_required()
def add_favorite(post_id):
    user_id=get_jwt_identity()
    if Favorite.query.filter_by(user_id=user_id,post_id=post_id).first() is not None:
        return jsonify({"msg":"用户已经收藏了该文章"}),400
    
    new_favorite=Favorite(user_id=user_id,post_id=post_id)
    
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.to_dict()), 201

# 取消收藏功能
@bp.route('/posts/<int:post_id>/favorites', methods=['DELETE'])
@jwt_required()  
def remove_favorite(post_id):
    user_id = get_jwt_identity()
    favorite_to_remove = Favorite.query.filter_by(user_id=user_id, post_id=post_id).first()
    if favorite_to_remove is None:
        return jsonify({"msg": "没有收藏过"}), 404
    
    db.session.delete(favorite_to_remove)
    db.session.commit()
    return jsonify({"msg": "成功取消收藏"}), 200



# 关注模块

@bp.route('/follow', methods=['POST'])
@jwt_required()
def follow():
    data = request.get_json()
    user_id = get_jwt_identity()
    to_follow_user_id = data.get('to_follow_user_id')

    if not user_id or not to_follow_user_id:
        return jsonify({"error": "缺少用户id或被关注者的id参数"}), 400
    
    user = User.query.filter_by(id=user_id).first()
    to_follow_user = User.query.filter_by(id=to_follow_user_id).first()

    if not user or not to_follow_user:
        return jsonify({"error": "用户不存在"}), 400


    if not user.is_following(to_follow_user):
        user.follow(to_follow_user)
        user.follow_num += 1 
        to_follow_user.fan_num += 1  
    else:
        return jsonify({"message": f"{user.username} 已经关注 {to_follow_user.username}"}), 200

    db.session.commit()
    return jsonify({"message": f"{user.username} 现在关注了 {to_follow_user.username}"}), 200


# 关注列表
@bp.route('/followers/<int:user_id>', methods=['GET'])
def followers(user_id):
    user = User.query.filter_by(id=user_id).first_or_404(description='没有该用户')
    following_list = [{"user_id":u.id,"username":u.username} for u in user.following]
    return jsonify({"followers": following_list}), 200


# 取消关注

@bp.route('/unfollow', methods=['POST'])
@jwt_required()  
def unfollow():
    data = request.get_json()
    user_id = get_jwt_identity()
    unfollow_user_id = data.get('unfollow_user_id')

    if not user_id or not unfollow_user_id:
        return jsonify({"error": "缺少用户id或被取消关注者的id参数"}), 400
    
    user = User.query.filter_by(id=user_id).first()
    unfollow_user = User.query.filter_by(id=unfollow_user_id).first()

    if not user or not unfollow_user:
        return jsonify({"error": "用户不存在"}), 400

    if user.is_following(unfollow_user):
        user.unfollow(unfollow_user)
        user.follow_num -= 1 
        unfollow_user.fan_num -= 1
    else:
        return jsonify({"message": f"{user.username} 并未关注 {unfollow_user.username}"}), 200

    db.session.commit()
    return jsonify({"message": f"{user.username} 已经取消关注 {unfollow_user.username}"}), 200


# 问答模块

# 问问题
@bp.route('/ask', methods=['POST'])
@jwt_required()  
def ask_question():
    user_id=get_jwt_identity()
    data=request.get_json()
    title = data.get('title')
    content = data.get('content') or '详细描述为空'
    
    if not title:
        return jsonify({"message:":"提出的问题需要填写"}),400

    question = Question(title=title, content=content, user_id=user_id)
    db.session.add(question)
    db.session.commit()
    return jsonify({
        "message":"用户的问题已被发布",
        "id":question.id,
        "user_id":user_id,
        "title":title,
        "content":content,
        "created_at":question.created_at
    }),200



# 回答问题

@bp.route('/answer/<int:question_id>', methods=['POST'])
@jwt_required()  
def answer_question(question_id):
    user_id=get_jwt_identity()
    data=request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({"message:":"回答的内容需要填写"}),400
        
    new_answer = Answer(content=content, user_id=user_id, question_id=question_id)
    db.session.add(new_answer)
    db.session.commit()
    return jsonify({
        "message":"用户成功回答该问题",
        "id":new_answer.id,
        "user_id":user_id,
        "answer_content":content,
        "created_at":new_answer.created_at
    }),200



# 查看点赞过的所有文章

@bp.route('/liked_posts', methods=['POST'])
@jwt_required()  
def liked_posts():
    user_id = get_jwt_identity()
    likes = Like.query.filter_by(user_id=user_id).all()
    post_ids = [like.post_id for like in likes]
    liked_posts = Post.query.filter(Post.id.in_(post_ids)).all()
    liked_posts_dicts = [post.to_dict() for post in liked_posts]
    return jsonify({
        'liked_posts': liked_posts_dicts,
    }), 200




#  查看收藏的所有文章

@bp.route('/favorited_posts', methods=['POST'])
@jwt_required()  
def favorited_posts():
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    post_ids = [favorite.post_id for favorite in favorites]
    favorited_posts = Post.query.filter(Post.id.in_(post_ids)).all()
    favorited_posts_dicts = [post.to_dict() for post in favorited_posts]
    return jsonify({
        'favorited_posts': favorited_posts_dicts,
    }), 200


# 从点赞过的文章中搜索
@bp.route('/liked_posts_search', methods=['POST'])
@jwt_required() 
def liked_posts_search():
    user_id = get_jwt_identity()
    likes = Like.query.filter_by(user_id=user_id).all()
    post_ids = [like.post_id for like in likes]
    data=request.get_json()
    search_query = data.get('key')
    liked_posts = Post.query.filter(Post.id.in_(post_ids))\
        .filter(Post.title.contains(search_query) | Post.content.contains(search_query))\
        .all()

    liked_posts_dicts = [post.to_dict() for post in liked_posts]

    return jsonify({
        'liked_search_results': liked_posts_dicts,
    }), 200



#  从收藏的所有文章中搜索
@bp.route('/favorited_posts_search', methods=['POST'])
@jwt_required()  
def favorited_posts_search():
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    post_ids = [favorite.post_id for favorite in favorites]
    data=request.get_json()
    search_query = data.get('key')
    favorited_posts = Post.query.filter(Post.id.in_(post_ids))\
        .filter(Post.title.contains(search_query) | Post.content.contains(search_query))\
        .all()

    favorited_posts_dicts = [post.to_dict() for post in favorited_posts]

    return jsonify({
        'favorited_search_results': favorited_posts_dicts,
    }), 200


