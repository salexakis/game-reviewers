from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


# App configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, 'instance', "games.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



### Initializations
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "warning"
login_manager.login_message = "Please sign in to view this page."


from application import routes



