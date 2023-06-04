import json
from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_qrcode import QRcode
from datetime import timedelta
from sqlalchemy_serializer import SerializerMixin #generuje z rezultatu zapytania słownik z parami klucz wartość

app = Flask(__name__, static_url_path="/static")
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/magazyn"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=5)

QRcode(app)
db = SQLAlchemy(app)
app.app_context().push()


class Employee(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    First_name = db.Column(db.String(255))
    Last_name = db.Column(db.String(255))
    Login = db.Column(db.String(255))
    Password = db.Column(db.String(255))
    Position = db.Column(db.String(255))
    Phone_number = db.Column(db.String(255))
    QR_code = db.Column(db.String(255))

    def __init__(self, first_name, last_name, login, password, position, phone_number, qr_code):
        self.First_name = first_name
        self.Last_name = last_name
        self.Login = login
        self.Password = password
        self.Position = position
        self.Phone_number = phone_number
        self.QR_code = qr_code


def get_user(username: str, password: str):
    data = Employee.query.filter_by(Login=username, Password=password).first()
    if data is None:
        return False
    else:
        return data.to_dict()


def check_permission():
    pass


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.permanent = True
        username = request.form["user"]
        password = request.form["password"]
        data = get_user(username, password)
        if data is not False:
            session['user'] = username
            return redirect(url_for('user', usr=username))
        else:
            return render_template("index.html", Error_log='Nie prawidłowy login lub hasło', solid='solid', border='5px', color='red')
    else:
        if "user" in session:
            return redirect(url_for("user", usr=session["user"]))

        return render_template("index.html", solid='none')


@app.route('/<usr>')
def user(usr):
    if "user" in session:
        return render_template('base.html', data=usr)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))


@app.route('/new_employee', methods=['GET', 'POST'])
def add():
    pass


@app.route('/all_employer', methods=['GET', 'POST'])
def all_employer():
    pass


@app.route('/mobile_app_api', methods=['POST'])
def api():
    if request.method == 'POST':
        user = request.get_json()
        username = user['Login']
        password = user['Password']
        data = get_user(username, password)
        if data is not False:
            return data
        else:
            return 'Wrong data!'
    return None


@app.route('/errors', methods=['POST'])
def raports():
    if request.method == 'POST':
        data = request.get_json()
        data = data['Raport']
        return 'Raport recived. Back to main screen'
    return None



@app.route('/scanner_api', methods=['POST'])
def scanner_api():
    pass


if __name__ == '__main__':
    app.run(host="0.0.0.0")