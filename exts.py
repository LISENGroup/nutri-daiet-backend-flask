# exts.py
# 避免自回环




from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

from flask_mail import Mail
mail=Mail()

from flask_login import LoginManager
login_manager=LoginManager()

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter=Limiter(key_func=get_remote_address)

from flask_jwt_extended import JWTManager
jwt=JWTManager()