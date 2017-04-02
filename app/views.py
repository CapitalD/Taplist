from flask import render_template, redirect, url_for
from . import app, db, login_manager, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from models import Location, Tap, Person
from forms import NewLocationForm, LoginForm, EditProfile

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
    return render_template("login.html", form=form)

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
        db.session.add(person)
        db.session.commit()
        return redirect(url_for("index"))
    person = Person.query.get_or_404(id)
    form.email.data = person.email
    return render_template('edit_profile.html',
                            title='Edit profile',
                            person=person,
                            form=form)
