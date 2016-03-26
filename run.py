#!flask/bin/python
"""App starter script.

This script starts up the development (local) web server.
Imports the app variable from our app package and invokes its run
method to start the server. The 'app' variable holds the Flask instance
"""

from app import app
app.run(debug=True)
