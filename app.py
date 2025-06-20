from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'yoursecretkey'

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Login manager setup (optional for user accounts)
login_manager = LoginManager()
login_manager.init_app(app)

# ---------- MODELS ----------

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.String(200))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200)) # hashed

# ---------- LOAD USER (only needed if using Flask-Login) ----------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- ROUTES ----------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/dashboard')
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome, {current_user.username}!"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# ---------- ADMIN LOGIN (using session, not Flask-Login) ----------

admin_hashed_password = generate_password_hash("admin123")

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and check_password_hash(admin_hashed_password, password):
            session['admin'] = True
            return redirect('/admin-panel')
        else:
            return 'Invalid login'
    return render_template('admin_login.html')

@app.route('/admin-panel')
def admin_panel():
    if not session.get('admin'):
        return redirect('/admin-login')

    products = Product.query.all()
    return render_template('admin_panel.html', products=products)

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']

        product = Product(name=name, price=price, description=description)
        db.session.add(product)
        db.session.commit()

        return redirect('/admin-panel')
    return render_template('add_product.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',port=10000)
   
