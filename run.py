# This file is used to start the app
from flaskblog import app	# imports app from __init__.py.

if __name__== '__main__':
	app.run(debug=True) # debug mode to check errors. Used to start the application. 

# __init__.py runs as soon as the application starts running