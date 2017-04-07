from flask import render_template, redirect, url_for, abort, jsonify, request
from . import app, db, login_manager, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from models import Location, Tap, Person, Brewery, Beer
from forms import NewLocationForm, LoginForm, EditProfile, TapKeg

@app.route('/')
def index():
    all_locations = Location.query.all()
    return render_template('index.html',
                            all_locations=all_locations)

@app.route('/location/<id>', methods=['GET'])
def view_location(id):
    location = Location.query.get_or_404(id)
    all_locations = Location.query.all()

    return render_template('view_location.html',
                            title=location.name,
                            location=location,
                            all_locations=all_locations)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Person.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user) #, remember=True)
                return redirect(url_for("index"))
    return render_template('login.html',
                            title='Log in',
                            form=form)

## ADMINISTRATION PAGES ##

@login_manager.user_loader
def user_loader(user_id):
    return Person.query.get(user_id)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for("index"))


@app.route('/location/new', methods=['GET','POST'])
@login_required
def add_location():
    if not current_user.is_admin:
        return abort(401)
    form = NewLocationForm()
    if form.validate_on_submit():
        location = Location(name=form.name.data, address=form.address.data)
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('view_location', id=location.id))
    return render_template('new_location.html',
                            title='Add location',
                            form=form)


@app.route('/person/<id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    form = EditProfile()
    if form.validate_on_submit():
        person = Person.query.get_or_404(id)
        person.email = form.email.data
        if len(form.password.data) > 0:
            person.password = bcrypt.generate_password_hash(form.password.data)
        if current_user.is_admin:
            person.is_admin = form.is_admin.data
            person.is_manager = form.is_manager.data
            person.is_brewer = form.is_brewer.data
        db.session.add(person)
        db.session.commit()
        return redirect(url_for("index"))
    person = Person.query.get_or_404(id)
    form.email.data = person.email
    return render_template('edit_profile.html',
                            title='Edit profile',
                            person=person,
                            form=form)

@app.route('/location/<id>/taps', methods=['GET'])
@login_required
def manage_taps(id):
    form = TapKeg()
    form.brewery.query = Brewery.query.order_by('name')
    form.beer.query = Beer.query.order_by('name')
    taps = Location.query.get_or_404(id).taps
    return render_template('manage_taps.html',
                            title='Manage taps',
                            taps=taps,
                            form=form)


@app.route('/tap/<id>/clear', methods=['GET'])
@login_required
def clear_tap(id):
    tap = Tap.query.get_or_404(id)
    tap.beer = None
    db.session.add(tap)
    db.session.commit()
    return redirect(url_for('manage_taps', id=tap.location.id))


@app.route('/tap/<id>/set', methods=['POST'])
@login_required
def tap_keg(id):
    tap = Tap.query.get_or_404(id)
    form = TapKeg(request.form)
    form.brewery.query = Brewery.query.order_by('name')
    form.beer.query = Beer.query.order_by('name')
    if form.validate_on_submit():
        tap.beer = form.beer.data
        db.session.add(tap)
        db.session.commit()
        return redirect(url_for('manage_taps', id=tap.location.id))
    return "didn't validate"

## AJAX ##

@app.route('/brewery/<id>/beers', methods=['GET'])
@login_required
def get_beers_by_brewery(id):
    brewery = Brewery.query.get_or_404(id)
    beers = [(b.id, b.name) for b in brewery.beers]
    return jsonify(beers)
