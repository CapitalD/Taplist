from . import db

class Tap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    beer_id = db.Column(db.Integer, db.ForeignKey('beer.id'))
    price_pint = db.Column(db.Float, default=0)
    price_tulip = db.Column(db.Float, default=0)
    price_jug = db.Column(db.Float, default=0)
    beer = db.relationship('Beer', backref='beer')

    def __repr__(self):
        return '<Tap %r>' % (self.label)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    taps = db.relationship('Tap', backref='location', lazy='dynamic')

    def __repr__(self):
        return '<Location %r>' % (self.name)

class Beer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    style = db.Column(db.String(255))
    abv = db.Column(db.Float)
    colour = db.Column(db.Integer)
    brewery_id = db.Column(db.Integer, db.ForeignKey('brewery.id'))
    brewery = db.relationship('Brewery', backref='brewery')
    taps = db.relationship('Tap', backref='taps', lazy='dynamic')

    def __repr__(self):
        return '<Beer %r>' % (self.name)

class Brewery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    beers = db.relationship('Beer', backref='beers', lazy='dynamic')

    def __repr__(self):
        return '<Brewery %r>' % (self.name)

# User is a reserved word for Postgres
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    authenticated = db.Column(db.Boolean, default=False, nullable=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<Person %r>' % (self.email)
