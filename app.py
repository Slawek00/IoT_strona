from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
from sqlalchemy_serializer import SerializerMixin #generuje z rezultatu zapytania słownik z parami klucz wartość
from qr_code_generator import Generator
import configparser
from password_gen import generate_password


#Konfiguracja parsera do pliku ustawień
config = configparser.ConfigParser()
config.read("config/config.ini")


#Konfiguracja aplikacji Flask
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/store"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = '2)4D)qk-y_CmYM8"8!zL>-@R8x.pj$'
app.permanent_session_lifetime = timedelta(minutes=5)


#Dołączenie bazy danych
db = SQLAlchemy(app)
app.app_context().push()


#Konfiguracja generatora kodów qr
generator = Generator()


#Modele tabel bazy danych
class pracownik(db.Model, SerializerMixin):
    ID = db.Column(db.Integer, primary_key=True)
    Imie = db.Column(db.String(20))
    Nazwisko = db.Column(db.String(255))
    Nr_Telefonu = db.Column(db.Integer)
    Posada = db.Column(db.String(20))
    Login = db.Column(db.String(20))
    Haslo = db.Column(db.String(20))
    url_QR = db.Column(db.String(20))

    def __init__(self, Imie, Nazwisko, Nr_Telefonu, Posada, Login, Haslo, url_QR):
        self.Imie = Imie
        self.Nazwisko = Nazwisko
        self.Nr_Telefonu = Nr_Telefonu
        self.Posada = Posada
        self.Login = Login
        self.Haslo = Haslo
        self.url_QR = url_QR


class pomieszczenia(db.Model, SerializerMixin):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nazwa = db.Column(db.String(100))
    Poziom_dostepu = db.Column(db.String(100))

    def __init__(self, Nazwa, Poziom_dostepu):
        self.Nazwa = Nazwa
        self.Poziom_dostepu = Poziom_dostepu


class wydarzenia(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Opis = db.Column(db.String(255))
    Data = db.Column(db.Date)

    def __init__(self, Opis, Data):
        self.Opis = Opis
        self.Data = Data


class raporty(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Opis = db.Column(db.String(255))
    Data = db.Column(db.Date)

    def __init__(self, Opis, Data):
        self.Opis = Opis
        self.Data = Data


#Funkcje aplikacji
def get_user(username: str, password: str):
    data = pracownik.query.filter_by(Login=username, Haslo=password).first()
    if data is None:
        return False
    else:
        return data.to_dict()


def check_permission(first_name: str, last_name: str, position: str, name: str):
    data = pracownik.query.filter_by(Imie=first_name, Nazwisko=last_name, Posada=position).first()
    data_permissions = pomieszczenia.query.filter_by(Nazwa=name, Poziom_dostepu=position).first()
    if data or data_permissions is None:
        return False
    else:
        return True


def new_employee(first_name, last_name, phone_number, position, login, password, url_QR):
    employee = pracownik(Imie=first_name, Nazwisko=last_name, Nr_Telefonu=phone_number, Posada=position,
                             Login=login, Haslo=password, url_QR=url_QR)
    db.session.add(employee)
    db.session.commit()


def new_report(description):
    date = str(datetime.utcnow())
    report = raporty(Opis=description, Data=date)
    db.session.add(report)
    db.session.commit()


def new_events(description):
    date = str(datetime.utcnow())
    event = wydarzenia(Opis=description, Data=date)
    db.session.add(event)
    db.session.commit()


def get_all():
    data = pracownik.query.all()
    return data


def get_all_events():
    data = wydarzenia.query.all()
    return data


def get_all_reports():
    data = raporty.query.all()
    return data


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.permanent = True
        username = request.form["user"]
        password = request.form["password"]
        data = get_user(username, password)
        data_events = get_all_events()
        if data is not False:
            session['user'] = username
            return redirect(url_for('user', usr=username, data=data_events))
        else:
            return render_template("index.html", Error_log='Nie prawidłowy login lub hasło', solid='solid', border='5px', color='red')
    else:
        data_events = get_all_events()
        if "user" in session:
            return redirect(url_for("user", usr=session['user'], data=data_events))

        return render_template("index.html", solid='none')


@app.route('/<usr>')
def user(usr):
    if "user" in session:
        data = get_all_events()
        return render_template('home.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/menu', methods=['POST'])
def menu():
    if request.method == 'POST':
        value = request.form["button"]
        match value:
            case "Home Page":
                data = get_all_events()
                return redirect(url_for('user', usr=session['user'], data=data))
            case "Employees":
                data = get_all()
                return render_template('all_employee.html', data=data)
            case "Add employee":
                return render_template('add.html')
            case "Reports":
                data = get_all_reports()
                return render_template('reports.html', data=data)
            case "Logout":
                return redirect(url_for('logout'))
            case other:
                pass
    else:
        pass


@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))


@app.route('/new_employee', methods=['POST'])
def add():
    if request.method == 'POST':
        data_events = get_all_events()
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone_number = request.form["phone_number"]
        position = request.form["position"]
        login = request.form["login"]
        if first_name and last_name and phone_number and position is not None:
            password_gen = generate_password(first_name)
            data = {
                'Imie': first_name,
                'Nazwisko': last_name,
                'Posada': position
            }
            name = first_name + " " + last_name
            image_url = generator.upload_image(name, data)
            new_employee(first_name, last_name, phone_number, position, login, password_gen, image_url)
            return redirect(url_for('user', usr=session['user'], data=data_events))
        else:
            data = get_all_events()
            return redirect(url_for('user', usr=session['user'], data=data))


@app.route('/mobile_app_api', methods=['POST'])
def api():
    if request.method == 'POST':
        user = request.get_json()
        username = user['Login']
        password = user['Password']
        data = get_user(username, password)
        if "user" in session:
            if session['user'] != username and data is not False:
                return data
            else:
                return "Wrong data or you must logout on desktop!"
        else:
            if data is not False:
                return data
            else:
                return "Wrong data!"
    return None


@app.route('/errors', methods=['POST'])
def reports():
    if request.method == 'POST':
        data = request.get_json()
        data_report = data['Report']
        new_report(data_report)
        return 'Report recived. Back to main screen'
    return None


@app.route('/events', methods=['POST'])
def events():
    if request.method == 'POST':
        data = request.get_json()
        event = data['Event']
        new_events(event)
        return "Events recived"
    return None


@app.route('/scanner_api', methods=['POST'])
def scanner_api():
    if request.method == 'POST':
        data = request.get_json()
        first_name = data['first_name']
        last_name = data['last_name']
        position = data['position']
        name = data['name']
        if check_permission(first_name, last_name, position, name) is True:
            return 'Open'
        else:
            return 'Permission denied!'
    return None


if __name__ == '__main__':
    app.run(host="0.0.0.0")