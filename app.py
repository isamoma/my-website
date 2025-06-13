from flask import Flask, render_template,request,redirect,url_for

app= Flask(__name__)
#Dummy user
USERNAME="admin"
PASSWORD="1234"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username==USERNAME and password==PASSWORD:
            return (url_for('welcome'))
    else:
        return render_template('login.html',error="Invalid credentials")
    
    return render_template('login.html')
@app.route('/welcome')
def welcome():
    return"Welcome! you are logged in,"

if __name__=="__main__":
    app.run(debug=True)