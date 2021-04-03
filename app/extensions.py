from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_travis import Travis
from flask_static_digest import FlaskStaticDigest

bcrypt = Bcrypt()
lm = LoginManager()
mail = Mail()
travis = Travis()
flask_static_digest = FlaskStaticDigest()
