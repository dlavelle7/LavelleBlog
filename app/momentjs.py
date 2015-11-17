# Moment.js wrapper class, invoked from the template

from jinja2 import Markup

class momentjs:

    def __call__(self, *args):
        return self.format(*args)

    def __init__(self, timestamp):
        self.timestamp = timestamp

    # Render method does not return a string, but instead wraps the
    # string inside a Markup object provided by Jinja2. 
    # This tells Jinja2 that the string should not be escaped
    def render(self, format):
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")

