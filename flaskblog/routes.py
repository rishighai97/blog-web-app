# This file acts as a controller
# It is used to create routes to every view in templates folder
# It is used for form validation along with forms.py
# It is used to use the models from models.py to store user and post info in database
import secrets # used to generate hex for image and password
import os # used for getting entire path of a file 
from PIL import Image # pip install Pillow. Used to compress image inorder to save space in application
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt # imported from __init__.py
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm # Form classes are imported and used by creating their objects and sending them to view to display the forms using Jinja templating
from flaskblog.models import User, Post # Models are imported from models.py to store data from the form in database
from flask_login import login_user, current_user, logout_user, login_required # current_user is used to access the user anywhere after they are logged in, login_user and logout_user are used to login and logout user respectively. login_required is used for route guarding. 


@app.route("/")
@app.route("/home") # routes for home page
def home():
	page = request.args.get('page',1,type=int) # 1 is default page number, get is search by id
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
	return render_template('home.html',posts=posts) # render template is used to display the page to be displayed when the route is called. posts is passed and displayed on home page using Jinja templating
    

@app.route("/about")
def about():
    return render_template('about.html',title='about') # title is set as About. Wherever know title is passed, default title is used

@app.route("/register",methods=['GET','POST'])
def register(): 
	if current_user.is_authenticated: # is user is authenticated, redirect him to home
		return redirect(url_for('home'))
	form = RegistrationForm() # An object of the Registration form is created. 
	if form.validate_on_submit(): # If the user hits the submit button, the form is validated based on the default and custom validators in the forms.py Registration class. If there are no errors, the code block below is executed
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') 
		user = User(username=form.username.data, email=form.email.data, password=hashed_password) # User info recieved from form is stored in User model from models.py
		db.session.add(user) # We use add method to add the user object filled with data into user(first letter lowercase of class User) table in sql alchemy db 
		db.session.commit() # We commit the changes to the database
		flash('Your account has been created! You are now able to log in','success') # flash message is displayed on login page and class is set as success to get a green message, which is done in layout.html
		return redirect(url_for('login')) # User is refirected to login page so that now they can login to the system
	return render_template('register.html',title='Register',form=form) # The form object is passed to the view and the components are displayed using jinja templating. If any errors are there, they are also displayed in the view (register.html)

@app.route("/login",methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first() # We check if the user with specified email is present 
		if user and bcrypt.check_password_hash(user.password, form.password.data): # If the user exists and the password matches with the password in db, user is authenticated
			login_user(user, remember=form.remember.data) # We accept yes/no from rememeber me boolean field
			next_page = request.args.get('next') # next arguement from the url is used to redirect the user to desired page if he directly tried to access a page via url 
			return redirect(next_page) if next_page else redirect(url_for('home')) # We redirect the user to home page after successful login
		else:
			flash('Login Unsuccessful. Please check username and password','danger') # If user is not authenticated, we display a flash message with class='danger' which is set in the layout.html
	return render_template('login.html',title='Login',form=form) 

@app.route("/logout")
def logout():
	logout_user() # logs out the user from login_manager system
	return redirect(url_for('home')) # User is redirected to home after logout


def save_picture(form_picture): # This method is used to save the profile picture in static/profile_pics folder. The image is hashed to a string as mentioned in models.py
	random_hex = secrets.token_hex(8) # A random hash string is generated say a112jkjskdjfg
	_, f_ext = os.path.splitext(form_picture.filename) # the extension is obtained. say jpeg from image.jpeg
	picture_fn = random_hex + f_ext # New image name is generated  a112jkjskdjfg.jpeg
	picture_path = os.path.join(app.root_path, 'static/profile_pics',picture_fn) # oath where the image has to be saved is obtained. (..../blog/flaskblog/static/profile_pics/a112jkjskdjfg.jpeg)

	output_size = (125, 125) # dimensions to which the image has to be resized
	i = Image.open(form_picture) # we open the image using open method from Image (Pillow/PIL package)
	i.thumbnail(output_size) # Thumbnail of the desired size is generated
	i.save(picture_path) # Picture is saved in desired location

	return picture_fn # picture filename is returned to be stored in database



@app.route("/account",methods=['GET','POST']) 
@login_required # This page is accessible if the user is logged in
def account():
	form = UpdateAccountForm() # Instance of form
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data) # if new image is uploaded, it is stored in the database
			current_user.image_file = picture_file # the image file uploaded is direclty stored in current_user and the data is automatically synched with sql database after commit
		current_user.username = form.username.data # new username is stored
		current_user.email = form.email.data # new email is stored
		db.session.commit() # commit updates the values changed in current_user in the database
		flash('Your account has been updated','success') # A message is flashed suggesting that updates where successful
		return redirect(url_for('account')) # post get redirect (avoid data will be resubmitted message)
	elif request.method == 'GET': # (Pre populating the fields)If the page is accessed in general, the original username and email are displayed.
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static',filename='profile_pics/'+current_user.image_file) # image file is also passed to the view (account.html)
	return render_template('account.html',title='Account',image_file=image_file, form=form) # (Populating the form in view)render the view and display error messages, if any


@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!','success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html',title=post.title,post=post)


@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403) # Forbidden page
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit() # Post is automatically committed as post object is synched with db table Post
		flash('Your post has been updated!','success')
		return redirect(url_for('post',post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html',title='Update Post',form=form,legend ='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403) # Forbidden page
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!','success')
	return redirect(url_for('home'))


@app.route("/user/<string:username>") # routes for home page
def user_posts(username):
	page = request.args.get('page',1,type=int) # 1 is default page number
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page=page,per_page=5)
	return render_template('user_posts.html',posts=posts, user=user) # render template is used to display the page to be displayed when the route is called. posts is passed and displayed on home page using Jinja templating
    