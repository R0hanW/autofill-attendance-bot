from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from databaseSetup  import User, Base
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xtnW2r1D44homkNMWLLt'

engine = create_engine('sqlite:///autofill.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
Session = DBSession()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/classes', methods = ['GET', 'POST'])
@login_required
def classes():
    if request.method == 'POST':
        user = Session.query(User).filter_by(id = current_user.get_id()).first()
        user.historyPeriod = request.form['historyPeriod']
        user.englishPeriod = request.form['englishPeriod']
        user.physicsPeriod = request.form['physicsPeriod']
        user.TOKPeriod = request.form['TOKPeriod']
        Session.add(user)
        Session.commit()
        return redirect(url_for('attendance'))
    return render_template("classes.html")

@app.route('/attendance')
@login_required
def attendance():
    day = date.today().strftime("%m/%d")
    return render_template("attendance.html", day = day)

@app.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        user = Session.query(User).filter_by(email = current_user.email).first()
        user.email = request.form['email']
        user.firstName = request.form['firstName']
        user.lastName = request.form['lastName']
        user.password = request.form['password']
        Session.add(user)
        Session.commit()
        return redirect(url_for('home'))
    return render_template("account.html")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = True if request.form.get('remember') else False
        user = Session.query(User).filter_by(email=email).first()

        if not user:
            flash('User does not exist. Click sign up to create a new user')
            return redirect(url_for('login'))
        elif user.password != password:
            flash('Incorrect password. Try again.')
            return redirect(url_for('login'))
        login_user(user, remember=remember)
        return redirect(url_for('home'))
    return render_template('login.html')

@login_manager.user_loader
def loadUser(userID):
    return Session.query(User).filter_by(id = userID).first()

@app.route('/signup', methods = ['GET' , 'POST'])
def signup():
    if request.method =='POST':
        email = request.form['email']
        password= request.form['password']
        confirmPass = request.form['confirmPass']
        firstName = request.form['firstName']
        lastName= request.form['lastName']
        fullName = firstName + " " + lastName
        user = Session.query(User).filter_by(email=email).first()
        if user:
            flash('This account already exists.')
            return redirect(url_for('signup'))
        else:
            newUser = User(email=email, firstName=firstName, lastName = lastName, fullName = fullName, password=password)
            Session.add(newUser)
            Session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

scheduler = BlockingScheduler()
@scheduler.scheduled_job('cron', day_of_week='mon-fri',hour=0)
def resetAttendance():
    users= Session.query(User).all()
    for user in users:
        user.historyAttendance = 0
        user.englishAttendance = 0
        user.physicsAttendance = 0
        user.TOKAttendance = 0
        user.attendance = 0
        Session.add(user)
        Session.commit()


@app.route('/users/json/17106742468711417621')
def usersJSON():
    users = Session.query(User).all()
    return jsonify(User =[i.serialize for i in users])

@app.route('/attendance/json/17106742468711417621', methods = ['GET', 'POST'])
def attendanceJSON():
    if(request.method == 'POST'):
        user = Session.query(User).filter_by(email = request.form['email']).first()
        user.historyAttendance = int(request.form['historyAttendance'])
        user.englishAttendance = int(request.form['englishAttendance'])
        user.physicsAttendance = int(request.form['physicsAttendance'])
        user.TOKAttendance = int(request.form['TOKAttendance'])
        user.attendance = int(request.form['attendance'])
        Session.add(user)
        Session.commit()
    return render_template("attendanceJSON.html")
"""@app.route('/login/forgot', methods = ['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':

    return render_template('forgotPassword.html')

@app.route('/<string:id>/change', methods = ['GET', 'POST'])
def changePassword(id):
    if request.method == 'POST':
        user = Session.query(User).filter_by(id = id)
        password = request.form['password']
        confirmPass = request.form['confirmPass']
        if(password != confirmPass):
            flash("Passwords do not match try again.")
            return redirect(url_for('change password'))
        generate_password_hash(password, method='sha256')
        session.add(user)
        session.commit()
        flash("Password has been successfully changed")
        return redirect(url_for('login'))
    return render_templace('changePassword.html')"""

if __name__ == '__main__':
    app.debug = True
    app.run()
    scheduler.start()
