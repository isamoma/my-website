from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Use a long random string in real apps

#Setup database
basedir =os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///"+
os.path.join(basedir,'database.dp')
app.config['SQLALACHEMY_TRACK_MODIFICATIONS']=
False

db =SQLAlchemy(app)

# Define the Product model
class Product (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<Product {self.name}>'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if username in users:
            return "Username already exists. Try a different one."

        # Hash password before saving
        hashed_password = generate_password_hash(password)
        users[username] = hashed_password
        save_users(users)

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Invalid username or password"

    return render_template('login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123': # You can change this
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return "Access denied: Invalid credentials"

    return render_template('admin_login.html')

@app.route('/admin-panel')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin.html'))

     products = Product.query.all()
     return render_template('admin_panel.html', products=products)
                            
# Temporary in-memory product list (will reset if app restarts)
products = []

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        product = Product(name=name,price=price,description=description)
        db.session.add(product)
        db.session.commit()

        products.append(product)
        return redirect(url_for('admin_panel'))

    return render_template('add_product.html')



@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/products')
def products():
    if 'username'in session:
        return render_template('products.html',username=session['username'])
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',port=10000)
