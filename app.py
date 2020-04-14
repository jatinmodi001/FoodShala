from flask import Flask, render_template, request,session,redirect,url_for, flash, Response
import os
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///KhaoPiyo.db'

db = SQLAlchemy(app)

#app.config['image_folder'] = os.path.join("static","images")

class menuItems(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable = False)
	price = db.Column(db.Float, default = 0)


class Users(db.Model):
	firstName = db.Column(db.String, nullable = False)
	lastName = db.Column(db.String)
	email = db.Column(db.String, primary_key = True)
	password = db.Column(db.String)
	mobile = db.Column(db.Integer)



@app.route("/")
def index():
	if 'email' in session:
		user = Users.query.filter_by(email=session['email']).first()
		return render_template("index.html",loggedIn=True,user=user)
	return render_template("index.html",loggedIn=False)


@app.route("/menu",methods=['GET'])
def menu():
	if 'email' in session:
		return render_template("menu.html",loggedIn=True)
	return redirect("/")

@app.route("/customerlogin",methods=['POST','GET'])
def login():

	if request.method == 'GET' and 'email' in session :
		return redirect("/")

	if request.method == 'POST':
		user = Users.query.filter_by(email=request.form['email']).first()
		if user is None:
			error = "User with this Email doesn't exists"
			return render_template("login.html",error=error)

		elif user.password != request.form['password']:
			error = "Your password is incorrect"

			return render_template("login.html",error=error)
		session['email'] = request.form['email']
		return redirect("/")

	return render_template("login.html")

@app.route("/signup",methods=['POST','GET'])
def signup():
	if request.method == 'POST':
		user = Users.query.filter_by(email=request.form['email']).first()
		if user is None:
			if request.form['password'] != request.form['confirmPassword']:
				return render_template("signup.html",error="Password must match")
			try:
				newUser = Users(email=request.form['email'],password=request.form['password'],firstName=request.form['firstName'],lastName=request.form['lastName'],mobile=request.form['mobile'])
				#print(newUser)
				db.session.add(newUser)
				db.session.commit()
				#session['email'] = newUser.email
				return Response('/')
			except:
				print("ERROR")
				return render_template('signup.html')
		else :
			return render_template("signup.html",error="User Already Exists")
	return render_template("signup.html")

def checkSession():
	if 'email' in session:
		return True
	return False

@app.route("/profile")
def profile():
	if checkSession():
		user = Users.query.filter_by(email=email).first()
		return render_template("profile.html",loggedIn=checkSession(),user=user)
	else :
		return redirect("/customerlogin")

@app.route("/logout")
def logout():
	session.pop("email",None)
	return redirect("/customerlogin")

def checkAdmin():
	if 'admin' in session:
		return True
	return False

@app.route("/admin",methods=['POST','GET'])
def admin():
	if checkAdmin():
		return render_template("admin.html")



@app.route("/restaurantlogin",methods=['POST','GET'])
def restaurantLogin():
	if request.method == 'POST':
		print(request.form)
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			session['admin'] = True
			return redirect("/admin")
	return render_template("restaurantLogin.html")

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)