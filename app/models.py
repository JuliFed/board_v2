from .main import db, bcrypt
from datetime import datetime, timedelta


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    limit_likes = db.Column(db.Integer)
    time_limit_like = db.Column(db.DateTime)
    adverts = db.relationship('Advert', backref='creator', lazy='dynamic')
    comments = db.relationship('Comment', backref='commentator', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.username = username
        pw_hash = bcrypt.generate_password_hash(password,5)
        self.password = pw_hash
        self.time_limit_like = datetime.utcnow() - timedelta(minutes=60)
        self.limit_likes = 5

    def minus_like(self):
        print(self.time_limit_like ,datetime.utcnow())
        if (self.time_limit_like + timedelta(minutes=60)) < datetime.utcnow():
            self.time_limit_like = datetime.utcnow()
            self.limit_likes = 5
        if self.limit_likes:
            self.limit_likes = self.limit_likes - 1
        db.session.add(self)
        db.session.commit()


class Advert(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    likes = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='comment', lazy='dynamic')
    # user = db.relationship('User', backref='creator', remote_side='user.id')
    
    def to_dict(self):
        record = {
            "id": self.id,
            "title": self.title,
            "timestamp": self.timestamp,
            "creator": User.query.get(self.user_id).username,
            "likes": self.likes,
            "comments": [ comment.to_dict() for comment in self.comments.all()]
        }
        return record

    def set_like(self):
        self.likes += 1
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_key(cls, key):
        s = cls.query.get(key)
        return s

   
class Comment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text_comment = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    advert_id = db.Column(db.Integer, db.ForeignKey('advert.id'))

    def to_dict(self):
        record = {
            "id": self.id,
            "body": self.text_comment,
            "timestamp": self.timestamp,
            "author": User.query.get(self.user_id).username,
        }
        return record

    @classmethod
    def get_by_key(cls, key):
        s = cls.query.get(key)
        return s
