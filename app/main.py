from flask import Flask, jsonify, request
from flask_jwt import JWT, jwt_required, current_identity
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import timedelta, datetime
from functools import wraps
from app import validator

try:
    from local_settings import *
except ImportError:
    pass

app = Flask(__name__)
app.config.from_object('app.config')
app.config.from_object('local_settings')
app.debug = True
database = SQLAlchemy(app)
db = database
bcrypt = Bcrypt(app)

from app import models


def authenticate(username, password):
    user = models.User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user


def identity(payload):
    user_id = payload['identity']
    user = models.User.query.get(user_id)
    return user


jwt = JWT(app, authenticate, identity)


def time_for_posting_comment(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        last_hour = datetime.utcnow() - timedelta(minutes=60)
        count_comm = models.Comment.query\
            .filter_by(user_id=current_identity.id, advert_id=kwargs['advert_id'])\
            .filter(models.Comment.timestamp >= last_hour)\
            .order_by(models.Comment.timestamp.desc())\
            .count()

        if count_comm >= app.config['LIKES_PER_HOUR_LIMIT']:
            # return kwargs['limit_by_count']=True
            return jsonify({"error": "You can't create comments greater than 5 of hour"}), 400
        return f(*args, **kwargs)
    return decorated_function


def time_for_posting_like(f):
    """
        Decorator for testing users rule sending likes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        limit_likes = current_identity.limit_likes
        time_limit = current_identity.time_limit_like
        if (time_limit + timedelta(minutes=60)) > datetime.utcnow() and not limit_likes:
            return jsonify({"error": "You can't like adverts greater then 5 in hour"}), 400
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['POST'])
def register_new_user():
    if request.method == 'POST':
        post_data = request.get_json()

        if not validator.register_data(json_data=post_data):
            return jsonify({"user_id": 'None', "error": "you must provide a valid data"}), 400
        password = post_data['password']
        if not models.User.query.filter_by(username=post_data['username']).first():
            new_user = models.User(username=post_data['username'], password=password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"user_id": new_user.id}), 201
        else:
            return jsonify({"user_id": None, "error": "this username has already been taken"}), 409


@app.route('/adverts', methods=['GET', 'POST'])
@jwt_required()
def adverts():
    if request.method == 'POST':
        post_data = request.get_json()

        if not validator.new_advert(post_data):
            return jsonify({"advert": 'None', "error": "you must provide a valid data"}), 400
        new_advert = models.Advert(
            title=post_data['data'],
            timestamp=datetime.utcnow(),
            creator=current_identity,
            likes=0
        )
        db.session.add(new_advert)
        db.session.commit()
        return jsonify({"advert_id":  new_advert.id}), 201

    all_adverts = models.Advert.query.all()
    if len(all_adverts) > 0:
        result = []
        for a in all_adverts:
            result.append(a.to_dict())
        return jsonify({"adverts": result}), 200
    else:
        return jsonify({"adverts": "None"}), 404


@app.route('/adverts/<int:advert_id>', methods=['POST'])
@jwt_required()
@time_for_posting_comment
def new_comment(advert_id):
    if request.method == 'POST':
        post_data = request.get_json()
        if not validator.new_comment(post_data):
            return jsonify({"comment": 'None', "error": "you must provide a valid data"}), 400
        advert_obj = models.Advert.query.get(advert_id)
        comment = models.Comment(
            text_comment=post_data["data"],
            timestamp=datetime.utcnow(),
            user_id=current_identity.id,
            advert_id=advert_obj.id
        )
        db.session.add(comment)
        db.session.commit()
        # return redirect('/adverts/%s/comments/%s' % (advert_id, comment.id)), 201
        return jsonify({"comment_id": comment.id}), 201

    return jsonify({"comment": None}), 500


@app.route('/adverts/<int:advert_id>', methods=['GET'])
@jwt_required()
def get_one_advert_with_comments(advert_id):
    advert = models.Advert.get_by_key(advert_id)
    if not advert:
        return jsonify({"advert": "None"}), 404
    return jsonify(advert.to_dict()), 200


@app.route('/adverts/<int:advert_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(advert_id):
    advert = models.Advert.get_by_key(advert_id)
    if not advert:
        return jsonify({"advert": "None"}), 404
    comments = advert.comments.all()
    if len(comments) > 0:
        result = []
        for c in comments:
            result.append(c.to_dict())
        return jsonify({"comments": result}), 200

    return jsonify({"comments": []}), 200


@app.route('/adverts/<int:advert_id>/like', methods=['POST'])
@jwt_required()
@time_for_posting_like
def like_advert(advert_id):
    if request.method == 'POST':
        models.Advert.query.get(advert_id).set_like()
        models.User.query.get(current_identity.id).minus_like()
        return jsonify({"like": True}), 200
    return jsonify({"comment": None}), 500




