from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
# add DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "qwerty"

# initialize DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create blog post model
class Posts (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))


# Create Model
class Users (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return ' <Name %r>' % self.name

#


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'password_hash2', message='Passwords must match!')])
    password_hash2 = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a class


class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/')
def index():
    first_name = "Mark"
    return render_template('index.html', first_name=first_name)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

# Custom error pages
# invalid url


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# internal server error


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # hash password
            hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(name=form.name.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User added successfully!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form,
                           name=name,
                           our_users=our_users)

# Create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted successfully!!!")
    return render_template('name.html',
                           name=name,
                           form=form)

# Create test pw page
@app.route('/test', methods=['GET', 'POST'])
def test():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
    # validate form
    if form.validate_on_submit():
        try:
            email = form.email.data
            password = form.password_hash.data
            # clear a form
            form.email.data = ''
            form.password_hash.data = ''

            pw_to_check = Users.query.filter_by(email=email).first()
            passed = check_password_hash(pw_to_check.password_hash, password)
        except:
            flash ('There is no such email, please return and try again!')
            return render_template('test.html',
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)

            
    

    return render_template('test.html',
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)

# Update db record


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated successfully")
            return render_template("update.html", form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem, try again")
            return render_template("update.html", form=form,
                                   name_to_update=name_to_update,
                                   id=id)
    else:
        return render_template("update.html", form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted Successfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form,
                               name=name,
                               our_users=our_users)
    except:
        flash("Whoops! There was a problem, try again!")
        return render_template('add_user.html', form=form,
                               name=name,
                               our_users=our_users)


if __name__ == "__main__":
    app.run(debug=True)
with app.app_context():
    db.create_all()
