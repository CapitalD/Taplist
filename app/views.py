from flask import render_template, redirect, url_for, abort, jsonify, request, flash
from . import app, db, login_manager, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from models import Location, Tap, Person, Brewery, Beer
from forms import NewLocation, LoginForm, ProfileForm, TapKeg, NewTap, NewBrewery, NewBeer, UploadBeerXML


@app.route('/')
def index():
    all_locations = Location.query.all()
    return render_template('index.html',
                            all_locations=all_locations)


@app.route('/location/<int:id>', methods=['GET'])
def view_location(id):
    location = Location.query.get_or_404(id)
    all_locations = Location.query.all()
    if request.args.get('fs') == '1':
        flash('Press ESC to exit fullscreen','info')
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
                login_user(user)
                flash("Log in successful", "success")
                return redirect(url_for("index"))
        else:
            flash("Incorrect email address or password. Please try again.", "error")
    if form.errors:
        flash("Incorrect email address or password.  Please try again.", "error")
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
    flash("Log out successful", "success")
    return redirect(url_for("index"))


@app.route('/location/new', methods=['GET','POST'])
@login_required
def add_location():
    if not current_user.is_admin:
        return abort(401)
    form = NewLocation()
    if form.validate_on_submit():
        location = Location(name=form.name.data, address=form.address.data)
        db.session.add(location)
        db.session.commit()
        flash("Location created successfully", "success")
        return redirect(url_for('manage_location', id=location.id))
    if form.errors:
        flash("Location could not be created. Please correct errors and try again.", "error")
    return render_template('new_location.html',
                            title='Add location',
                            form=form,
                            admin_template=True)


@app.route('/person/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    if not current_user.is_admin and not current_user.id == id:
        abort(401)
    form = ProfileForm()
    form.location.query = Location.query.order_by('name')
    form.brewery.query = Brewery.query.order_by('name')
    if form.validate_on_submit():
        person = Person.query.get_or_404(id)
        person.firstname = form.firstname.data
        person.lastname = form.lastname.data
        person.email = form.email.data
        if len(form.password.data) > 0:
            person.password = bcrypt.generate_password_hash(form.password.data)
        if current_user.is_admin:
            person.is_admin = form.is_admin.data
            person.is_manager = form.is_manager.data
            person.is_brewer = form.is_brewer.data
        db.session.add(person)
        db.session.commit()
        if person.is_manager:
            location = Location.query.get(form.location.data.id)
            location.managers.append(person)
            db.session.add(location)
            db.session.commit()
        if person.is_brewer:
            brewery = Brewery.query.get(form.brewery.data.id)
            brewery.brewers.append(person)
            db.session.add(brewery)
            db.session.commit()
        flash("Profile edited successfully", "success")
        return redirect(url_for("index"))
    person = Person.query.get_or_404(id)
    form.firstname.data = person.firstname
    form.lastname.data = person.lastname
    form.email.data = person.email
    if person.is_manager:
        form.location.data = person.locations[0]
    if person.is_brewer:
        form.brewery.data = person.breweries[0]
    if form.errors:
        flash("Changes to profile could not be saved.  Please correct errors and try again.", "error")
    return render_template('edit_profile.html',
                            title='Edit profile',
                            person=person,
                            form=form,
                            admin_template=True)


@app.route('/location/taps/edit', methods=['GET'])
@app.route('/location/<int:id>/taps/edit', methods=['GET', 'POST'])
@login_required
def manage_location(id=None):
    if current_user.is_manager and id and not [i for i in current_user.locations if i.id == id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_manager:
        return abort(401)
    keg_form = TapKeg()
    new_tap_form = NewTap()
    keg_form.brewery.query = Brewery.query.order_by('name')
    keg_form.beer.query = Beer.query.order_by('name')
    if keg_form.tap_keg.data and keg_form.validate_on_submit():
        tap = Tap.query.get_or_404(keg_form.tap_id.data)
        tap.beer = keg_form.beer.data
        db.session.add(tap)
        db.session.commit()
    if keg_form.errors:
        flash('An error occurred when trying to tap the keg.  Please try again.','error')
    if new_tap_form.add_tap.data and new_tap_form.validate_on_submit():
        location = Location.query.get_or_404(id)
        new_tap = Tap(label=new_tap_form.label.data, location=location)
        db.session.add(new_tap)
        db.session.commit()
        flash("Tap added successfully", "success")
    if new_tap_form.errors:
        flash("A new tap couldn't be added. Please try again.", "error")
    if current_user.is_admin:
        manageable_locations = Location.query.all()
    elif current_user.is_manager:
        manageable_locations = Location.query.filter(Location.managers.any(id=current_user.id)).all()
    if id:
        location = Location.query.get_or_404(id)
    else:
        location = manageable_locations[0]
    return render_template('manage_location.html',
                            title='Manage taps',
                            location=location,
                            taps=location.taps,
                            keg_form=keg_form,
                            new_tap_form=new_tap_form,
                            manageable_locations=manageable_locations,
                            admin_template=True)


@app.route('/tap/<int:id>/clear', methods=['GET'])
@login_required
def clear_tap(id):
    tap = Tap.query.get_or_404(id)
    if current_user.is_manager and not [i for i in current_user.locations if i.id == tap.location.id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_manager:
        return abort(401)
    tap.beer = None
    db.session.add(tap)
    db.session.commit()
    return redirect(url_for('manage_location', id=tap.location.id))


@app.route('/location/<int:loc_id>/tap/<int:tap_id>/delete', methods=['GET'])
@login_required
def delete_tap(loc_id, tap_id):
    location = Location.query.get_or_404(loc_id)
    if current_user.is_manager and not [i for i in current_user.locations if i.id == location.id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_manager:
        return abort(401)
    tap = Tap.query.get_or_404(tap_id)
    if tap in location.taps:
        db.session.delete(tap)
        db.session.commit()
        flash("Tap removed successfully.", "success")
        return redirect(url_for('manage_location', id=location.id))
    flash("That tap couldn't be removed for some reason.", "error")
    return redirect(url_for('manage_location', id=location.id))


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
        flash("Brewery created successfully", "success")
        return redirect(url_for('manage_beers', id=brewery.id))
    if form.errors:
        flash("The brewery couldn't be added. Please try again.", "error")
    return render_template('new_brewery.html',
                            title='Add brewery',
                            form=form,
                            admin_template=True)

@app.route('/brewery/beers/edit', methods=['GET'])
@app.route('/brewery/<int:id>/beers/edit', methods=['GET'])
@login_required
def manage_beers(id=None):
    if current_user.is_brewer and id and not [i for i in current_user.breweries if i.id == id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_brewer:
        return abort(401)
    form = NewBeer()
    upload_beerXML = UploadBeerXML()
    if current_user.is_admin:
        manageable_locations = Brewery.query.all()
    elif current_user.is_brewer:
        manageable_locations = Brewery.query.filter(Brewery.brewers.any(id=current_user.id)).all()
    if id:
        brewery = Brewery.query.get_or_404(id)
    else:
        brewery = manageable_locations[0]
    return render_template('manage_beers.html',
                            title="Manage beers",
                            brewery=brewery,
                            new_beer=form,
                            edit_beer=form,
                            upload_beerXML=upload_beerXML,
                            manageable_locations=manageable_locations,
                            admin_template=True)


@app.route('/brewery/<int:id>/beer/new', methods=['POST'])
@login_required
def new_beer(id):
    if current_user.is_brewer and not [i for i in current_user.breweries if i.id == id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_brewer:
        return abort(401)
    brewery = Brewery.query.get_or_404(id)
    new_beer = NewBeer(request.form)
    if new_beer.validate_on_submit():
        beer = Beer(name=new_beer.name.data,
                        style=new_beer.style.data,
                        abv=new_beer.abv.data,
                        colour=new_beer.colour.data,
                        brewery=brewery)
        db.session.add(beer)
        db.session.commit()
        flash("Beer created successfully", "success")
        return redirect(url_for('manage_beers', id=brewery.id))
    edit_beer = NewBeer()
    flash("The new beer couldn't be created. Please try again.", "error")
    return render_template('manage_beers.html',
                            title="Manage beers",
                            brewery=brewery,
                            new_beer=new_beer,
                            edit_beer=edit_beer,
                            admin_template=True)


@app.route('/beer/<int:id>/edit', methods=['POST'])
@login_required
def edit_beer(id):
    beer = Beer.query.get_or_404(id)
    if current_user.is_brewer and not [i for i in current_user.breweries if i.id == beer.brewery.id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_brewer:
        return abort(401)
    edit_beer = NewBeer(request.form)
    if edit_beer.validate_on_submit():
        beer.name = edit_beer.name.data
        beer.style = edit_beer.style.data
        beer.abv = edit_beer.abv.data
        beer.colour =  edit_beer.colour.data
        db.session.add(beer)
        db.session.commit()
        flash("Beer updated successfully", "success")
        return redirect(url_for('manage_beers', id=beer.brewery.id))
    new_beer = NewBeer()
    flash("Changes to the beer could not be saved. Please try again.", "error")
    return render_template('manage_beers.html',
                            title="Manage beers",
                            brewery=beer.brewery,
                            new_beer=new_beer,
                            edit_beer=edit_beer,
                            admin_template=True)


@app.route('/beer/<int:id>/delete', methods=['GET'])
@login_required
def delete_beer(id):
    beer = Beer.query.get_or_404(id)
    if current_user.is_brewer and not [i for i in current_user.breweries if i.id == beer.brewery.id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_brewer:
        return abort(401)
    brewery_id = beer.brewery.id
    db.session.delete(beer)
    db.session.commit()
    flash("Beer removed successfully.", "success")
    return redirect(url_for('manage_beers', id=brewery_id))


@app.route('/person/new', methods=['GET', 'POST'])
@login_required
def new_person():
    if not current_user.is_admin:
        return abort(401)
    form = ProfileForm()
    form.location.query = Location.query.order_by('name')
    form.brewery.query = Brewery.query.order_by('name')
    if form.validate_on_submit():
        person = Person(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        email=form.email.data,
                        password = bcrypt.generate_password_hash(form.password.data),
                        is_admin = form.is_admin.data,
                        is_manager = form.is_manager.data,
                        is_brewer = form.is_brewer.data)
        db.session.add(person)
        db.session.commit()
        if person.is_manager:
            location = Location.query.get(form.location.data.id)
            location.managers.append(person)
            db.session.add(location)
        if person.is_brewer:
            brewery = Brewery.query.get(form.brewery.data.id)
            brewery.brewers.append(person)
            db.session.add(brewery)
        db.session.commit()
        flash("Person added successfully", "success")
        return redirect(url_for("index"))
    if form.errors:
        flash("Changes to profile could not be saved.  Please correct errors and try again.", "error")
    return render_template('new_person.html',
                    title='Add a person',
                    form=form,
                    admin_template=True)


@app.route('/brewery/edit', methods=['GET', 'POST'])
@app.route('/brewery/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def manage_brewery(id=None):
    if current_user.is_brewer and id and not [i for i in current_user.breweries if i.id == id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_brewer:
        return abort(401)
    form = NewBrewery(request.form)
    if form.validate_on_submit():
        brewery = Brewery.query.get_or_404(id)
        brewery.name = form.name.data
        brewery.address = form.address.data
        db.session.add(brewery)
        db.session.commit()
        flash("Brewery updated successfully", "success")
        return redirect(url_for('manage_beers', id=brewery.id))
    if current_user.is_admin:
        manageable_locations = Brewery.query.all()
    elif current_user.is_brewer:
        manageable_locations = Brewery.query.filter(Brewery.brewers.any(id=current_user.id)).all()
    if id:
        brewery = Brewery.query.get_or_404(id)
    else:
        brewery = manageable_locations[0]
    form.name.data = brewery.name
    form.address.data = brewery.address
    return render_template('manage_brewery.html',
                            title="Manage brewery",
                            form=form,
                            brewery=brewery,
                            manageable_locations=manageable_locations,
                            admin_template=True)


@app.route('/location/edit', methods=['GET', 'POST'])
@app.route('/location/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_location(id=None):
    if current_user.is_manager and id and not [i for i in current_user.locations if i.id == id]:
        return abort(401)
    if not current_user.is_admin and not current_user.is_manager:
        return abort(401)
    form = NewLocation(request.form)
    if form.validate_on_submit():
        location = Location.query.get_or_404(id)
        location.name = form.name.data
        location.address = form.address.data
        db.session.add(location)
        db.session.commit()
        flash("Location updated successfully", "success")
        return redirect(url_for('manage_location', id=location.id))
    if current_user.is_admin:
        manageable_locations = Location.query.all()
    elif current_user.is_manager:
        manageable_locations = Location.query.filter(Location.managers.any(id=current_user.id)).all()
    if id:
        location = Location.query.get_or_404(id)
    else:
        location = manageable_locations[0]
    form.name.data = location.name
    form.address.data = location.address
    return render_template('edit_location.html',
                            title="Manage location",
                            form=form,
                            location=location,
                            manageable_locations=manageable_locations,
                            admin_template=True)

## AJAX ##

@app.route('/brewery/<int:id>/beers.json', methods=['GET'])
@login_required
def get_beers_by_brewery(id):
    brewery = Brewery.query.get_or_404(id)
    beers = [(b.id, b.name) for b in brewery.beers.order_by('name')]
    return jsonify(beers)

@app.route('/beer/<int:id>/detail.json', methods=['GET'])
@login_required
def get_beer_details(id):
    beer = Beer.query.get_or_404(id)
    b = [(beer.id, beer.name, beer.style, beer.abv, beer.colour)]
    return jsonify(b)

@app.route('/brewery/<int:id>/beer/new/upload', methods=['POST'])
@login_required
def upload_beerXML(id):
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file_stream = request.files['file']
    return file_stream.read()
