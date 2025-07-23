# ai回答

from flask import (
    Blueprint,request,json
)

import markdown2


# ai蓝图
bp=Blueprint("ai",__name__,url_prefix="/ai")


@bp.route('/response',methods=['POST'])
def ai():
    data=request.get_json()
    food_name = data.get('food_name')
    user_info = data.get('user_info')
    import new_chat
    output=new_chat.handle_food_info_get(food_name, user_info)
    return output,200


