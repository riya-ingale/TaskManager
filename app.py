from flask import Flask, redirect, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask import session, g
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL').replace('postgres://', 'postgresql://')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(300), nullable=False)
    password = db.Column(db.String(300), nullable=False)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    content = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        user = Users.query.filter_by(id=session['user']).first()
        g.user = user

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'
# login_manager.login_message = "You need to Login first"


# @login_manager.user_loader
# def load_user(user_id):
#     return Users.query.get(int(user_id))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method="sha256")
        cpassword = request.form['cpassword']

        user = Users.query.filter_by(email=email).first()
        if user:
            flash("User Name Already Exists, Choose another one")
            return redirect("/signup")

        if(password == cpassword):
            new_user = Users(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash("Sucessfully Registered!")
            return redirect('/login')
        else:
            flash("Passwords don't match")
            return redirect("/signup")

    return render_template("signup.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        session.pop('user', None)
        # logout_user()
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email).first()
        if not user:
            flash("No such User found, Try Signing Up First")
            return redirect("/signup")
        if user:
            if check_password_hash(user.password, password):
                session['user'] = user.id
                # login_user(user)
                return redirect('/')
            else:
                flash("Incorrect password")
                return redirect("login")
    return render_template("login.html")


# @app.route('/logout')
# def logout():
#     logout_user()
#     flash("Successfully Logged out!")
#     return redirect('/login')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user', None)
    flash("Sucessfully Logged Out")
    return render_template('login.html')


@app.route('/', methods=['POST', 'GET'])
# @login_required
def home():
    if g.user:
        if request.method == 'POST':
            task_content = request.form['content']
            new_task = Todo(content=task_content, user_id=g.user.id)
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                return "There was a problem while adding Your Task"
        else:
            tasks = Todo.query.filter_by(
                user_id=g.user.id).order_by(Todo.date_created)
            return render_template("index.html", tasks=tasks)
    else:
        flash("You need to Login First")
        return redirect('/login')


@app.route('/delete/<int:id>')
def delete(id):
    task_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem while deleting the Task"


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            flash("There was a problem while updating your Task")
            return redirect(f'/update/{task.id}')
    else:
        # GET request
        return render_template('update.html', task=task)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
