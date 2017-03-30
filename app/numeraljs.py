from jinja2 import Markup

class numeraljs(object):
    def __init__(self, float):
        self.float = float

    def render(self, format):
        return Markup("<script>\ndocument.write(numeral(\"%s\").%s);\n</script>" % (self.float, format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def currency(self):
        return self.render("format('$0,0.00')")

    def decimal_if_required(self):
        return self.render("format('0[.]00')")
