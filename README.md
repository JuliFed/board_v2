Advert's board
==============

About
----------------
Rest api for creating a custom advert board.
Authorized users can create announcements, add comments (no more than 5 per hour), put like.

Technologies:
-----------
- Flask
- SQlAlchemy
- Flask-JWT

Installation
----------------------------
    git clone https://github.com/JuliFed/board_v2.git
    cd board_v2
    pip install -r requirements.txt

You must configure the paths to the database in file **local_settings-example.py**
and create app.db with command:

    python app/db_create.py

Run server:

    python run.py 

Postman documentation
---------------------------
<https://documenter.getpostman.com/view/4511244/adverts/RWEZT3Vb>

For testing you can use postman collection with requests - it is in directory postman.
