from flask import render_template
from . import app, db
from models import Location, Tap

@app.route('/')
def index():
    all_locations = Location.query.all()
    return render_template("index.html",
                            all_locations=all_locations)

@app.route('/location/<id>', methods=['GET'])
def view_location(id):
    location = Location.query.get_or_404(id)
    all_locations = Location.query.all()

    return render_template('view_location.html',
                            title=location.name,
                            location=location,
                            all_locations=all_locations)
