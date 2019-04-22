# This file holds all the imports and configuration variables
# This file runs as soon as app starts running. All the variables are set and available for use in the application

from flask import Flask # flask
from flask_sqlalchemy import SQLAlchemy # flask-sqlalchemy
from flask_bcrypt import Bcrypt # flask-bcrypt
from flask_login import LoginManager # flask-login

app = Flask(__name__) # app variable is used to work with the application
app.config['SECRET_KEY'] = 'a7fe8c8d1996c015d442cb0db82d82b3' # Secret key is used to avoid csrf attacks. Used to initialize form in layout.html hidden_tag()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Location to store sqlite database named site.db
db = SQLAlchemy(app) # used to connect application to database
bcrypt = Bcrypt(app) # used to generate hash strings for storing password in database in routes file
login_manager = LoginManager(app) # Used to manage the user login, session and logout. 
login_manager.login_view = 'login' # Used to redirect user to login if trying to access a page without logging in (route guarding)
login_manager.login_message_category = 'info' # Used to set the class for message displayed on login page to log in before trying to access a page

from flaskblog import routes # routes file is imported and run