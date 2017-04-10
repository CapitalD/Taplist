from flask import render_template, redirect, url_for, abort, jsonify, request
from . import app, db, login_manager, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from models import Location, Tap, Person, Brewery, Beer
from forms import NewLocationForm, LoginForm, EditProfile, TapKeg, NewTap, NewBrewery, NewBeer


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


@app.route('/location/<id>/taps/edit', methods=['GET'])
@login_required
def manage_taps(id):
    keg_form = TapKeg()
    new_tap_form = NewTap()
    keg_form.brewery.query = Brewery.query.order_by('name')
    keg_form.beer.query = Beer.query.order_by('name')
    location = Location.query.get_or_404(id)
    return render_template('manage_taps.html',
                            title='Manage taps',
                            location=location,
                            taps=location.taps,
                            keg_form=keg_form,
                            new_tap_form=new_tap_form)


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
    keg_form = TapKeg(request.form)
    keg_form.brewery.query = Brewery.query.order_by('name')
    keg_form.beer.query = Beer.query.order_by('name')
    if keg_form.tap_keg.data and keg_form.validate_on_submit():
        tap.beer = keg_form.beer.data
        db.session.add(tap)
        db.session.commit()
        return redirect(url_for('manage_taps', id=tap.location.id))
    return "didn't validate"


@app.route('/location/<loc_id>/tap/new', methods=['POST'])
@login_required
def new_tap(loc_id):
    location = Location.query.get_or_404(loc_id)
    new_tap_form = NewTap(request.form)
    if new_tap_form.add_tap.data and new_tap_form.validate_on_submit():
        new_tap = Tap(label=new_tap_form.label.data, location=location)
        db.session.add(new_tap)
        db.session.commit()
        return redirect(url_for('manage_taps', id=new_tap.location.id))


@app.route('/location/<loc_id>/tap/<tap_id>/delete', methods=['GET'])
@login_required
def delete_tap(loc_id, tap_id):
    location = Location.query.get_or_404(loc_id)
    tap = Tap.query.get_or_404(tap_id)
    if tap in location.taps:
        db.session.delete(tap)
        db.session.commit()
        return redirect(url_for('manage_taps', id=location.id))


@app.route('/brewery/new', methods=['GET', 'POST'])
@login_required
def new_brewery():
    if not current_user.is_admin:
        return abort(401)
    form = NewBrewery()
    if form.validate_on_submit():
        brewery = Brewery(name=form.name.data, address=form.address.data)
        db.session.add(brewery)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_brewery.html',
                            title='Add brewery',
                            form=form)


@app.route('/brewery/<id>/beers/edit', methods=['GET'])
@login_required
def manage_beers(id):
    if not current_user.is_admin and not current_user.is_brewer:
        return abort(401)
    form = NewBeer()
    brewery = Brewery.query.get_or_404(id)
    return render_template('manage_beers.html',
                            title="Manage beers",
                            brewery=brewery,
                            new_beer=form,
                            edit_beer=form)

@app.route('/brewery/<brewery_id>/beer/new', methods=['POST'])
@login_required
def new_beer(brewery_id):
    brewery = Brewery.query.get_or_404(brewery_id)
    new_beer = NewBeer(request.form)
    if new_beer.validate_on_submit():
        beer = Beer(name=new_beer.name.data,
                        style=new_beer.style.data,
                        abv=new_beer.abv.data,
                        colour=new_beer.colour.data,
                        brewery=brewery)
        db.session.add(beer)
        db.session.commit()
        return redirect(url_for('manage_beers', id=brewery.id))
    edit_beer = NewBeer()
    return render_template('manage_beers.html',
                            title="Manage beers",
                            brewery=brewery,
                            new_beer=new_beer,
                            edit_beer=edit_beer)

@app.route('/beer/<id>/edit', methods=['POST'])
@login_required
def edit_beer(id):
    beer = Beer.query.get_or_404(id)
    edit_beer = NewBeer(request.form)
    if edit_beer.validate_on_submit():
        beer.name = edit_beer.name.data
        beer.style = edit_beer.style.data
        beer.abv = edit_beer.abv.data
        beer.colour =  edit_beer.colour.data
        db.session.add(beer)
        db.session.commit()
        return redirect(url_for('manage_beers', id=beer.brewery.id))
    new_beer = NewBeer()
    return render_template('manage_beers.html',
                            title="Manage beers",
                            brewery=beer.brewery,
                            new_beer=new_beer,
                            edit_beer=edit_beer)


## AJAX ##

@app.route('/brewery/<id>/beers.json', methods=['GET'])
@login_required
def get_beers_by_brewery(id):
    brewery = Brewery.query.get_or_404(id)
    beers = [(b.id, b.name) for b in brewery.beers]
    return jsonify(beers)

@app.route('/beer/<id>/detail.json', methods=['GET'])
@login_required
def get_beer_details(id):
    beer = Beer.query.get_or_404(id)
    b = [(beer.id, beer.name, beer.style, beer.abv, beer.colour)]
    return jsonify(b)
