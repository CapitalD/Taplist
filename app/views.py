from flask import render_template
from . import app, db
from models import Location, Tap

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/location/<id>', methods=['GET'])
def view_location(id):
    location = Location.query.get_or_404(id)
    return render_template('view_location.html',
                            title=location.name,
                            location=location)
