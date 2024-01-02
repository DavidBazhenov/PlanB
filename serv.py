import babel
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_restful import Api, Resource, reqparse
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from ImageToText import img_to_text
import cv2
import os
from wtforms.validators import InputRequired
from flask_babel import Babel
import pyrebase

import firebase_admin
from firebase_admin import credentials
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

UPLOAD_FOLDER = r"C:\Users\david\PycharmProjects\planb\uploads"
cred = credentials.Certificate("planbusersdata-firebase-adminsdk-24e05-4a325c008c.json")
firebase_admin.initialize_app(cred)

fireconfig = {
    "apiKey": "AIzaSyCDlRnlbYqfQ0zpQqSl4GSQ5RXXtE03p_g",
    "authDomain": "planbusersdata.firebaseapp.com",
    "databaseURL": "https://planbusersdata-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "planbusersdata",
    "storageBucket": "planbusersdata.appspot.com",
    "messagingSenderId": "164014046685",
    "appId": "1:164014046685:web:ab51419d7805bdc2638a34",
    "measurementId": "G-VYQXK4YCD1"
}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def photo_to_text(path):
    img = cv2.imread(path)
    text = img_to_text("rus", img)
    os.remove(path)
    return text


def allowed_file(filename):
    print(filename.split('.', 1)[1].lower())
    return '.' in filename and \
        filename.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_locale():
    return request.accept_languages.best_match(['en'])

def isLogged():
    try:
        if current_user.is_authenticated():
            return "True"
    except:
        return "False"
app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LANGUAGES'] = ['en', 'ru']

babel = Babel(app)
babel.init_app(app, locale_selector=get_locale)

firebase = pyrebase.initialize_app(fireconfig)
# db = firebase.database()
auth = firebase.auth()

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return UserLogin().fromDB(user_id, auth)


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/', methods=['GET'])
def home():
    try:
        if current_user.is_authenticated():
            return render_template('main.html', isLogged="True")
    except:
        return render_template('main.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('mail')
    password = request.form.get('password')
    try:
        # Регистрация пользователя
        user = auth.sign_in_with_email_and_password(email, password)
        flash('Login successful', 'success')
        userlogin = UserLogin().create(user)
        login_user(userlogin)
    except:
        print("Login err")
        return render_template('main.html', loger="True", isLogged="False")

    return render_template('main.html', isLogged="True", success="True")

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return render_template('main.html', isLogged="False")

# Обработка отправленной формы "Form 2"
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    mail = request.form.get('mail')
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        # Регистрация пользователя
        user = auth.create_user_with_email_and_password(mail, password)
        flash('Register successful', 'success')
        userlogin = UserLogin().create(user)
        login_user(userlogin)
    except:
        return render_template('main.html', loger="True", isLogged="False")

    return render_template('main.html', isLogged="True", success="True")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('method_not_allowed.html'), 405


@app.route('/tryapi')
@login_required
def tryapi():
    return render_template('api.html', isLogged=isLogged())


@app.route('/docs')
@login_required
def docs():
    return render_template('docs.html', isLogged=isLogged())


@app.route('/convertor', methods=['POST', 'GET'])
@login_required
def convert():
    form = UploadFileForm()
    text = "the answer will appear here..."
    text2 = "File is not supported!"
    if form.validate_on_submit():
        file = form.file.data  # First grab the file

        if allowed_file(file.filename):
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                   secure_filename(file.filename)))  # Then save the file
            print(file.filename)
            text = photo_to_text(f"C:\\Users\\david\\PycharmProjects\\planb\\uploads\\{file.filename}")
            return render_template('convertor.html', form=form, text=text, change_style=True, isLogged=isLogged())
        else:
            return render_template('convertor.html', form=form, text=text2, isLogged=isLogged())
    return render_template('convertor.html', form=form, text=text, isLogged=isLogged())


@app.route('/api', methods=['POST'])
def new():
    photo = request.get_json()['img']

    photo_data = base64.b64decode(photo)

    with open("compare.jpg", "wb") as file:
        file.write(photo_data)
    text = photo_to_text("compare.jpg")
    return {"text": text}


if __name__ == '__main__':
    app.run(debug=True, port=3000, host="127.0.0.1")
