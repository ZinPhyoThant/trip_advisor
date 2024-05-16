from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from flask_bcrypt import Bcrypt #pip install Flask-Bcrypt = https://pypi.org/project/Flack-Bcrypt/

from werkzeug.utils import secure_filename

import os

import re

from models import db, User, Tour, Booking

app = Flask(__name__)

app.config['SECRET_KEY'] = 'zinphyothant-40685582'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
# Database configuration mysql  Username:password@hostname/databasename
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/tripadvisor'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

bcrypt = Bcrypt(app)

db.init_app(app)

with app.app_context():
    db.create_all()

app.config['UPLOAD_FOLDER'] = 'static/images'

ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


# Routes
@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods =['GET','POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form : 
        fullname = request.form['username']
        password = request.form['password']
        email = request.form['email']
   
        user_exists = User.query.filter_by(email=email).first() is not None

        if user_exists:
            mesage = 'Email already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not fullname or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = User(username=fullname, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            mesage = 'You have successfully registered!'
            
    elif request.method == 'POST':
        mesage = "Please fill out the form!"
    return render_template('register.html', mesage = mesage)

@app.route('/login', methods=['GET','POST'])
def login():
    mesage = ''
    if request.method == 'POST':
        email =  request.form['email']
        password = request.form['password']
        # print(email)
        # print(password)

        if email == '' or password == '':
            mesage = 'Please enter email and password!'
        else:
            user = User.query.filter_by(email=email).first()
            print(user)

            if user is None:
                mesage = 'Email not found!'
            else:
                if not bcrypt.check_password_hash(user.password, password):
                    mesage = 'Please enter correct email and password!'
                else:
                    session['loggedin'] = True
                    session['userid'] = user.id
                    session['name'] = user.username
                    session['email'] = user.email

                if email == 'admin@gmail.com':
                    mesage = 'Admin logged in successfully!'
                    return redirect(url_for('dashboard'))
                else:
                    mesage = 'User logged in successfully!'
                    return redirect(url_for('customer'))
                    
        # if email == '' or password == '':
        #     mesage = 'Please enter email and password!'
        # else: 
        #     user = User.query.filter_by(email='admin@gmail.com').first()
        #     print(user)
                
        #     if user is None:
        #         mesage = 'Access restricted to admin only!'
                
        #     else:
        #         if not bcrypt.check_password_hash(user.password, password):
        #             mesage = 'Please enter correct email and password!'
        #         else:
        #             session['loggedin'] = True
        #             session['userid'] = user.id
        #             session['name'] = user.username
        #             session['email'] = user.email
        #             mesage = 'Logged in successfully !'
        #         return redirect(url_for('dashboard'))

    return render_template('login.html', mesage = mesage)
    

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    if 'loggedin' in session:
        tours = Tour.query.all()

        return render_template("dashboard.html",tours = tours)
    return redirect(url_for('login'))

@app.route("/customer", methods=['GET','POST'])
def customer():
    if 'loggedin' in session:
        tours = Tour.query.all()

        return render_template("customer.html",tours = tours)
    return redirect(url_for('login'))

@app.route("/tours", methods = ['GET','POST'])
def tours():
    if 'loggedin' in session:
        tours = Tour.query.all()

        return render_template("tours.html", tours = tours)
    return redirect(url_for('login'))


@app.route('/save_tour', methods=['POST'])
def save_tour():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']

            action = request.form['action']

            if action == 'updateTour':
                id = request.form['id']
                tour = Tour.query.get(id)

                tour.name = name
                tour.description = description
                tour.price = price
                
                
                db.session.commit()
                print("UPDATE tour")
            else:
                file = request.files['uploadFile']
                filename = secure_filename(file.filename)
                print(filename)
                if file and allowed_file(file.filename):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    filenameimage = file.filename

                    tour = Tour(name=name, picture=filenameimage,description=description, price=price)
                    db.session.add(tour)
                    db.session.commit()
                    print("INSERT INTO Tour")
                else:
                    msg = 'Invalid upload only png, jpg, jped, gif'
            return redirect(url_for('tours'))
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return render_template("tours.html", msg=msg)
    return redirect(url_for('login'))

# @app.route('/book_tour', methods=['POST'])
# def book_tour():
#     msg = ''
#     if 'loggedin' in session:
#         tours = Tour.query.all()

#         return render_template("tours.html", tours = tours)
#     return redirect(url_for('login'))

@app.route("/edit_tour", methods =['GET', 'POST'])
def edit_tour():
    msg = ''    
    if 'loggedin' in session:
        id = request.args.get('id')
        print(id)
        tours = Tour.query.get(id)
         
        return render_template("edit_tours.html", tours = tours)
    return redirect(url_for('login'))


@app.route("/delete_tour", methods =['GET'])
def delete_tour():
    if 'loggedin' in session:
        id = request.args.get('id')
        tour = Tour.query.get(id)
        print(tour.picture)
        db.session.delete(tour)
        db.session.commit()
        os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], tour.picture))
        return redirect(url_for('tours'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
