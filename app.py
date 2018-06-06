from flask import Flask, jsonify, request, redirect, Response
from flask_jwt import JWT, jwt_required, current_identity
from datetime import timedelta, datetime
from functools import wraps
import validator
import models
from settings import app, db, bcrypt


def authenticate(username, password):
    user = models.User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user


def identity(payload):
    user_id = payload['identity']
    user = models.User.query.get(user_id)
    return user


jwt = JWT(app, authenticate, identity)


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
        new_advert = models.Advert(title=post_data['data'], timestamp=datetime.utcnow(), creator=current_identity)
        db.session.add(new_advert)
        db.session.commit()
        return redirect('/adverts/%s' % new_advert.id), 201

    all_adverts = models.Advert.query.all()
    if len(all_adverts) > 0:
        result = []
        for a in all_adverts:
            result.append(a.to_dict())
        return jsonify({"adverts": result}), 200
    else:
        return jsonify({"adverts": "None"}), 404


# def count_comments_by_last_hour(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         print(kwargs.get('advert_id'))
#         print(current_identity.id)
#         advert = mongo.db.Adverts.find_one({"_id": ObjectId(kwargs.get('advert_id'))}, {"comments": True})
#         comments = advert['comments']
#         # for comment in cursor:
#         print(comments)
#         #     comments.append(comment)
#         # print(comments)
#
#         return f(*args, **kwargs)
#
#     return decorated_function
#
#
@app.route('/adverts/<advert_id>', methods=['POST'])
@jwt_required()
# @count_comments_by_last_hour
def new_comments(advert_id):
    if request.method == 'POST':
        post_data = request.get_json()
        if not validator.new_comment(post_data):
            return jsonify({"comment": 'None', "error": "you must provide a valid data"}), 400
        advert_obj = models.Advert.query.get(advert_id)
        new_comment = models.Comment(body=post_data["data"], timestamp=datetime.utcnow(), user_id=current_identity, advert_id=advert_obj)
        db.session.add(new_comment)
        db.session.commit()
        return redirect('/adverts/%s' % advert_id), 201

    return jsonify({"comment": None}), 500
#

@app.route('/adverts/<advert_id>', methods=['GET'])
@jwt_required()
def get_one_advert_with_comments(advert_id):
    advert = models.Advert.get_by_key(advert_id)
    if not advert:
        return jsonify({"advert": "None"}), 404
    return jsonify(advert.to_dict()), 200


if __name__ == '__main__':
    app.run()
