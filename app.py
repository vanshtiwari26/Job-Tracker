from flask import Flask,render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,UserMixin,logout_user,login_required
# this is imp bcz this help us to store our password in database in unreadable from so data will protect
from werkzeug.security import generate_password_hash , check_password_hash
#  use to check only one persson take a single uname 
from sqlalchemy.exc import IntegrityError
# for more security we import os 
import os 
#  when we import this then we no need to pass user to templates
from flask_login import current_user



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdata.db'
#  this will break the server on render 
# app.config['SECRET_KEY'] = os.urandom(24)  # here why 24 bcz its standard size
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret-key")

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

# usermixin was very imp for login
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),unique=True,nullable=False)
    password = db.Column(db.String(200),nullable=False)

class job(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    company =db.Column(db.String(200),nullable=False)  
    role =db.Column(db.String(100),nullable=False)  
    status =db.Column(db.String(50),default="Applied")  
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/")
def home():
    return render_template('base.html')

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        uname = request.form['uname']
        password = request.form['password']
        user = User(username=uname,password=generate_password_hash(password)) # this create password in unreadable form
        
        try:
         db.session.add(user)
         db.session.commit()
         flash("Your Registration is Done",'success')
         return redirect ("/login")
        except IntegrityError:
            db.session.rollback()
            flash("Username already taken", "danger")
            return redirect("/register") 
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        uname=request.form['uname']
        password=request.form['password']
        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password , password):
            login_user(user)
            flash("Welcome to the page",'success')
            return redirect("/")
        else:
            flash("Your Credential was Incorrect",'warning')
            return redirect("/login")   
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Will Success",'success')
    return redirect('/login')

@app.route("/dashboard")
@login_required
def dash():
    jobs = job.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html',jobs=jobs)

@app.route('/addjob',methods=['GET','POST'])
@login_required
def addjob():
    if request.method=="POST":
      company= request.form['company']
      role= request.form['role']
      status = request.form['status']
      data=job(company=company,role=role,status=status,user_id=current_user.id)
      db.session.add(data)
      db.session.commit()
      return redirect ('/dashboard')
    return render_template("add_job.html")  

@app.route("/edit/<int:id>",methods=['GET','POST'])
@login_required
def edit(id):
    data=job.query.get_or_404(id)
    if request.method=='POST':
     company=request.form['company']
     role=request.form['role']
     status=request.form['status']
     data.company=company
     data.role=role
     data.status=status
     db.session.commit()
     return redirect('/dashboard')
    return render_template('edit.html',data=data)

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    data = job.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    return redirect("/dashboard")



if __name__ == "__main__":
    app.run(debug=True)