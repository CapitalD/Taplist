from . import db

class Tap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    def __repr__(self):
        return '<Tap %r>' % (self.label)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    taps = db.relationship('Tap', backref='location', lazy='dynamic')

    def __repr__(self):
        return '<Location %r>' % (self.name)
