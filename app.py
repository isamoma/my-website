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

from datetime import datetime

class UserProfile(db.Model, UserMixin):
    __tablename__ = 'userr_profile'
    __table_args__ = {'extend_existing': True} # 👈 add this line

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200)) # hashed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ---------- MODELS ----------

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.String(200))

from app import db, UserProfile
from werkzeug.security import generate_password_hash

# Create admin user
admin_user = UserProfile(
    username='admin',
    password=generate_password_hash('admin123')
)

# Add to database
db.session.add(admin_user)
db.session.commit()

print("✅ Admin user created successfully!")



# ---------- LOAD USER (only needed if using Flask-Login) ----------

@login_manager.user_loader
def load_user(user_id):
    return UserProfile.query.get(int(user_id))

# ---------- ROUTES ----------
@app.route("/")
def index():
   return redirect('index.html')

@app.route('/post')
@login_required
def post():
        pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserProfile.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin:
                return redirect('/admin-panel')
            return redirect('/dashboard')
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and check_password_hash(username, password):
            login_user(UserProfile.query.filter_by(username='admin').first())
            return redirect('/admin-panel')
        else:
            return 'Invalid login'
    return render_template('admin_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = UserProfile.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists!"

        hashed_password = generate_password_hash(password)
        new_user = UserProfile(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect('/dashboard')
        
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',current_user=current_user)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html',user=current_user)

@app.route('/products')
@login_required
def product():
    return render_template('products.html',username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/admin-panel')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return "Access Denied", 403
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

        from werkzeug.security import generate_password_hash
        admin_user=UserProfile(username="admin",password=generate_password_hash("admin123"))
        db.session.add(admin_user)
        db.session.commit()
                                
        



    app.run(host='0.0.0.0',port=10000)   
