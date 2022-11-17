from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
# add DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "qwerty"

# initialize DB
db = SQLAlchemy(app)

# Create Model
class Users (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(200), nullable=False)
    email =db.Column(db.String(120), nullable=False, unique=True)
    date_added =db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return' <Name %r>' % self.name

#
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
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
    name=None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, 
                         email = form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data=''
        form.email.data=''
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


if __name__ == "__main__":
    app.run(debug=True)
with app.app_context():
    db.create_all()