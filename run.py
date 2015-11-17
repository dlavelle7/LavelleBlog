#!flask/bin/python
from app import app
app.run(debug = True)

# Run scripts starts up the development (local) web server.
# Imports the app variable from our app package and invokes its run
# method to start the server.
# The app variable holds the Flask instance
