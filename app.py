from flask import Flask, render_template, request,session,redirect,url_for, flash, Response
import os
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, ForeignKey, update
from datetime import datetime
app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///FoodShala.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Items(db.Model):
	__tablename__ = 'items'
	restaurantId = db.Column(db.Integer,ForeignKey('restaurants.id'))
	restaurantName = db.Column(db.String)
	id = db.Column(db.Integer,primary_key=True)
	dishtype = db.Column(db.String)
	name = db.Column(db.String)
	price = db.Column(db.Float)
	veg = db.Column(db.Boolean)

class Restaurants(db.Model):
	__tablename__ = 'restaurants'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String)
	ownerFirstName = db.Column(db.String)
	ownerLastName = db.Column(db.String)
	email = db.Column(db.String)
	address = db.Column(db.String)
	password = db.Column(db.String)
	mobile = db.Column(db.String)

class Users(db.Model):
	__tablename__ = 'users'
	firstName = db.Column(db.String, nullable = False)
	lastName = db.Column(db.String)
	email = db.Column(db.String, primary_key = True)
	password = db.Column(db.String)
	mobile = db.Column(db.Integer)
	address = db.Column(db.String)
	veg = db.Column(db.Boolean)

class Cart(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	user = db.Column(db.String,ForeignKey('users.email'))
	itemId = db.Column(db.Integer,ForeignKey('items.id'))

class OrderHistory(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	user = db.Column(db.String,ForeignKey('users.email'))
	itemId = db.Column(db.Integer,ForeignKey('items.id'))
	restaurantId = db.Column(db.Integer,ForeignKey('restaurants.id'))
	date = db.Column(db.DateTime,default=datetime.utcnow)



db.create_all()


#-----------------------------------------SESSION VALIDATORS-----------------------------------

def checkSession():
	if 'email' in session:
		return True
	return False

def checkRestaurant():
	if 'restaurant' in session:
		return True
	return False


#-------------------------------------------CUSTOMER ROUTES---------------------------------------

@app.route("/home")
def home():
	user = None
	restaurants = Restaurants.query.all()
	if checkSession():
		user = Users.query.filter_by(email=session['email']).first()
	return render_template("home.html",user=user,restaurants=restaurants)
	return redirect("/customerlogin")

@app.route("/menu",methods=['GET'])
def menu():
	items = Items.query.order_by(desc(Items.dishtype)).all()
	return render_template("menu.html",items=items,user=checkSession())


@app.route("/customerlogin",methods=['POST','GET'])
def login():
	if checkSession() or checkRestaurant():
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
	if checkSession() or checkRestaurant():
		return redirect("/")
	if request.method == 'POST':
		user = Users.query.filter_by(email=request.form['email']).first()
		if user is None:
			if request.form['password'] != request.form['confirmPassword']:
				return render_template("signup.html",error="Password must match")
			if len(request.form['mobile']) < 10:
				return render_template("signup.html",error="Mobile Number Invalid")
			veg = False
			if request.form['category'] == 'veg':
				veg = True
			try:
				newUser = Users(email=request.form['email'],password=request.form['password'],firstName=request.form['firstName'],lastName=request.form['lastName'],mobile=request.form['mobile'],veg=veg,address=request.form['address'])
				#print(newUser)
				db.session.add(newUser)
				db.session.commit()
				#session['email'] = newUser.email
				flash("Account Created")
				return redirect("/customerlogin")
			except:
				return render_template('signup.html',error="Internal Server Error")
		else :
			return render_template("signup.html",error="User Already Exists")
	return render_template("signup.html")

@app.route("/profile")
def profile():
	if checkSession():
		email = session['email']
		user = Users.query.filter_by(email=email).first()
		return render_template("profile.html",loggedIn=checkSession(),user=user)
	else :
		return redirect("/customerlogin")


@app.route("/add_to_cart",methods=['POST'])
def addToCart():
	if checkSession():
		temp = request.get_json()
		print(temp)
		itemId = temp['itemId']
		restaurantId = temp['restaurantId']
		user = session['email']
		cart = Cart.query.filter_by(itemId=itemId).first()
		if cart is None:
			cart = Cart(itemId=itemId,user=user)
			try:
				db.session.add(cart)
				db.session.commit()
			except ValueError:
				print(ValueError)
			return ({'message' : 'Item Added In Your Cart'})
		else : 
			return ({'message' : 'Item Already In Your Cart'})
	return ({'message':'Login First'})

@app.route("/usercart",methods=['GET'])
def userCart():
	if checkSession():
		cartItems = Cart.query.with_entities(Cart.itemId).filter_by(user=session['email']).all()
		#items = Items.query.filter_by(id=cartItems[0][0]).all()
		cart = []
		for x in cartItems:
			cart.append(x[0])
		items = Items.query.filter(Items.id.in_(cart)).all()
		totalPrice = 0
		for x in items:
			totalPrice += x.price
		#items = Items.query.filter_by(id in )
		return render_template("userCart.html",items=items,user=checkSession(),totalPrice=totalPrice)
	return redirect("/")

@app.route("/orderhistory")
def orderHistory():
	if checkSession():
		orderhistory = OrderHistory.query.filter_by(user=session['email']).order_by(desc(OrderHistory.date)).all()
		
		items = []
		for x in orderhistory:
			temp = Items.query.filter_by(id=x.itemId).first()
			items.append((temp,x.date.strftime("%d/%m/%Y, %H:%M:%S")))
		return render_template("orderHistory.html",user=checkSession(),orders=orderhistory,items=items)

@app.route("/placeorder",methods=['POST'])
def placeOrder():
	if checkSession():
		cartItems = Cart.query.with_entities(Cart.itemId).filter_by(user=session['email']).all()
		cart = []
		for x in cartItems:
			cart.append(x[0])
		items = Items.query.filter(Items.id.in_(cart)).all()
		newOrder = []
		for x in items:
			db.session.add(OrderHistory(user=session['email'],itemId=x.id,restaurantId=x.restaurantId))
		try : 
			db.session.commit()
		except:
			return ({'message' : 'Internal Server Error'})
		flash("Order Placed")
		return redirect("/orderhistory")
	return redirect("/")


@app.route("/restaurant/<id>")
def restaurantMenu(id):
	items = Items.query.filter_by(restaurantId=id).order_by(desc(Items.dishtype)).all()
	restaurant = Restaurants.query.filter_by(id=id).first()
	return render_template("restaurantMenu.html",user=checkSession(),items=items,restaurant=restaurant)



@app.route("/deletefromcart",methods=['POST'])
def deleteFromCart():
	if checkSession():
		id = request.get_json()
		user = session['email']
		Cart.query.filter_by(user=user,itemId=id).delete()
		try : 
			db.session.commit()
		except :
			return ({'message' : 'Internal Server Error'})
		return ({'message' : 'Item deleted from cart'})
	return ({'message' : 'Unauthorized'})

#--------------------------------RESTAURANT ROUTES--------------------------------------


@app.route("/add_dish",methods=['POST','GET'])
def add():
	if checkRestaurant():
		if request.method == 'POST':
			temp = request.form
			name = temp['name'].lower()
			dishtype = temp['type'].lower()
			price = temp['price']
			restaurantId = session['restaurant']
			restaurantName = session['restaurantName']
			veg = False
			if temp['category'] == 'Veg':
				veg = True
			items = Items.query.filter_by(restaurantId=restaurantId,name=name).first()
			if items is None:
				newdish = Items(name=name,dishtype=dishtype,price=price,restaurantId=restaurantId,restaurantName=restaurantName,veg=veg)
				try:
					db.session.add(newdish)
					db.session.commit()
				except :
					return render_template("/addDish.html",error="Internal Server Error")
				flash("Dish Added")
				return redirect("/items")
			else :
				return render_template("/addDish.html",error="Dish Already Contains In Your Menu")
		return render_template("/addDish.html")
	return redirect("/")


@app.route("/restaurantsignup",methods=['POST','GET'])
def RestaurantSignup():
	if checkRestaurant() or checkSession():
		return redirect("/")
	error = None
	if request.method == 'POST':
		temp = request.form;
		restaurant = Restaurants.query.filter_by(email=temp['email']).first()
		if restaurant is None:
			if temp['password'] != temp['confirmPassword']:
				error = 'Password Must Match'
				return render_template("restaurantSignup.html",error=error)
			if len(temp['mobile']) < 10:
				error = 'Invalid Mobile Number'
				return render_template("restaurantSignup.html",error=error)
			print("NOT EXIST")
			name = temp['name']
			ownerFirstName = temp['firstName']
			ownerLastName = temp['lastName']
			password = temp['password']
			email = temp['email']
			mobile = temp['mobile']
			address = temp['address']
			try : 
				newRestaurant = Restaurants(name=name,ownerFirstName=ownerFirstName,ownerLastName=ownerLastName,
										email=email,mobile=mobile,address=address,password=password)
				db.session.add(newRestaurant)
				db.session.commit()
			except ValueError:
				print(ValueError)
				error = 'Internal Server Error'
			flash("Account Created")
			return redirect("/restaurantlogin")
		else:
			error = 'Restaurant with this email already exists'
	return render_template("restaurantSignup.html",error=error)


@app.route("/restaurantDetails")
def admin():
	if checkRestaurant():
		restaurant = Restaurants.query.filter_by(id=session['restaurant']).first()
		return render_template("restaurantDetails.html",restaurant=restaurant)
	return redirect("/restaurantlogin")

@app.route("/items")
def items():
	if checkRestaurant():
		id = session['restaurant']
		print('ID = ',id)
		items = Items.query.filter_by(restaurantId=id).all()
		return render_template("Items.html",items=items)
	return redirect("/")

@app.route("/restaurantlogin",methods=['POST','GET'])
def restaurantLogin():
	if checkSession() or checkRestaurant():
		return redirect('/')
	if request.method == 'POST':
		restaurant = Restaurants.query.filter_by(email=request.form['email']).first()
		if restaurant is None:
			error = "Restaurant with this email doesn't exists"
			return render_template("restaurantLogin.html",error=error)
		if restaurant.password != request.form['password']:
			error = 'Your password is incorrect'
			return render_template("restaurantLogin.html",error=error)
		session['restaurant'] = restaurant.id
		session['restaurantName'] = restaurant.name
		return redirect("/restaurantDetails")
	return render_template("restaurantLogin.html")


@app.route("/deleteitem",methods=["POST"])
def deleteItem():
	if checkRestaurant():
		items = Items.query.filter_by(id=request.get_json()).delete()
		try:
			db.session.commit()
		except : 
			return ({'data' : 'Error Occured'})
		return ({"data" : "deleted"})
	return redirect("/")


@app.route("/totalorders")
def totalOrders():
	if checkRestaurant():
		orders = OrderHistory.query.filter_by(restaurantId=session['restaurant'])
		total = []
		for x in orders:
			total.append((x,Users.query.filter_by(email=x.user).first(), Items.query.filter_by(id=x.itemId).first()))
		return render_template("totalOrders.html",orders=total)
	return redirect("/")


#--------------------------------------COMMON ROUTES-------------------------------------

@app.route("/logout")
def logout():
	session.pop("email",None)
	session.pop("restaurant",None)
	return redirect("/")


@app.route("/")
def index():
	if checkSession():
		user = Users.query.filter_by(email=session['email']).first()
		return render_template("index.html",user=user)
	if checkRestaurant():
		return redirect('/restaurantDetails')
	return render_template("index.html")

#---------------------------------------------------------------------------------------------
if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(debug=True,port=port)