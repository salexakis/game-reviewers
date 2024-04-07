from application import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    profile_image = db.Column(db.String(30), nullable=False, default='default_profile_image.png')
    password = db.Column(db.String(15), nullable=False)
    games = db.relationship('Game', backref='reviewer', lazy=True)

    def __repr__(self):
        return f"{self.username}:{self.email}"



class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    review = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(40), default='default_game_image.png')
    rating = db.Column(db.Integer, default=1, nullable=False)
    review_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"{self.review_date}:{self.title}:{self.rating}"
