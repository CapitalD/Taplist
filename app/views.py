from flask import render_template, redirect, url_for
from . import app, db
from models import Location, Tap
from forms import NewLocationForm

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

## ADMINISTRATION PAGES ##

@app.route('/location/new', methods=['GET','POST'])
def add_location():
    form = NewLocationForm()
    if form.validate_on_submit():
        location = Location(name=form.name.data, address=form.address.data)
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('view_location', id=location.id))
    return render_template('new_location.html',
                            title='Add location',
                            form=form)
