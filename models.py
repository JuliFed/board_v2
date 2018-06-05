from settings import db, bcrypt
from sqlalchemy import inspect


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    adverts = db.relationship('Advert', backref='creator', lazy='dynamic')
    comments = db.relationship('Comment', backref='commentator', lazy='dynamic')
    
    def __init__(self, username, password):
        self.username = username
        pw_hash = bcrypt.generate_password_hash(password,5)
        self.password = pw_hash

    
class Advert(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='comment', lazy='dynamic')
    # user = db.relationship('User', backref='creator', remote_side='user.id')
    
    def to_dict(self):
        record = {
            "id": self.id,
            "title": self.title,
            "timestamp": self.timestamp,
            "creator": User.query.get(self.user_id).username,
            "comments": self.comments.all()
        }
        return record

    @classmethod
    def get_by_key(cls, key):
        s = cls.query.get(key)
        return s

   
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    advert_id = db.Column(db.Integer, db.ForeignKey('advert.id'))
    #
    # def to_dict(self):
    #     record = {
    #         "id": self.id,
    #         "body": self.body,
    #         "timestamp": self.timestamp,
    #         "creator": User.query.get(self.user_id).username,
    #     }
    #     return record
    #
    # def __repr__(self):
    #     return self.to_dict()
    #
    # @classmethod
    # def get_by_key(cls, key):
    #     s = cls.query.get(key)
    #     return s
