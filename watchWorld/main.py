import sqlite3
import os
from flask import Flask, render_template, request, redirect, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager, login_user
from UserLogin import UserLogin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLAlCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    dbase = getUser(user_id)
    return UserLogin().fromDB(user_id, dbase)

DATABASE = 'user.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,"user.db")))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db_conn = connect_db()
    with app.open_resource("sq_db.sql", mode="r") as f:
        db_conn.cursor().executescript(f.read())
    db_conn.commit()
    db_conn.close()

def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db

def checkUser(email):
    db_conn = get_db()
    __cur = db_conn.cursor()

    try:
        __cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
        res = __cur.fetchone()
        if res['count'] > 0:
            return True
        else:
            return False
    except:
        return True

def getUser(user_id):
    db_conn = get_db()
    __cur = db_conn.cursor()

    try:
        __cur.execute(f"SELECT * FROM users WHERE id = '{user_id}' LIMIT 1")
        res = __cur.fetchone()
        if not res:
            return False

        return res
    except:
        return False

def getUserByEmail(email):
    db_conn = get_db()
    __cur = db_conn.cursor()

    try:
        __cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
        res = __cur.fetchone()
        if not res:
            return False

        return res
    except:
        return False

#DB

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    lName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=False)

    def __init__(self, name , lName, email, password, country, is_active):
        self.name = name
        self.lName = lName
        self.email = email
        self.password = password
        self.country = country
        self.is_active = is_active

    def __repr__(self):
        return "<Users %r" % self.id % self.is_active

# link
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/workingProcess")
def workingProcess():
    return render_template("workingProcess.html")

@app.route("/registration", methods=["POST", "GET"])
def registration():
    if(request.method == "POST"):
        if(len(request.form["name"]) >= 4) and (len(request.form["lName"]) >= 4) and \
        (len(request.form["email"]) >= 4) and (len(request.form["password"]) > 4) and \
        (len(request.form["password2"]) > 4):
            if(request.form["password"] == request.form["password2"]):
                email = request.form["email"]
                dBase = checkUser(email)

                if(dBase == False):
                    hash = generate_password_hash(request.form["password"])

                    name = request.form["name"]
                    lName = request.form["lName"]
                    country = request.form["country"]

                    user = Users(name, lName, email,
                                hash, country, True)

                    try:
                        db.session.add(user)
                        db.session.commit()
                        return redirect("/")
                    except:
                        return "Arajacela xnidir"
                else:
                    return render_template("registration.html", dBase=dBase,
                            error="Այս էլփոստի հասցեն արդեն գոյություն ունի")
            else:
                dBase = True
                return render_template("registration.html", dBase=dBase,
                                       error="Գաղտնաբառը հաստատված չէ")
        else:
            dBase = True
            return render_template("registration.html", dBase=dBase,
                                error="Դաշտերում նիշերի թվաքանակը պետք է լինի 4-ից մեծ")
    else:
        return render_template("registration.html")

@app.route("/sing_in", methods=["POST", "GET"])
def sing_in():
    if(request.method == "POST"):
        user = getUserByEmail(request.form["email"])
        if(user and check_password_hash(user["password"], request.form["password"])):
            userLogin = UserLogin().create(user)
            login_user(userLogin)
            return render_template("index.html")
        else:
            return render_template("sing_in.html")
    else:
        return render_template("sing_in.html")


if(__name__ == "__main__"):
    app.run(debug=True)