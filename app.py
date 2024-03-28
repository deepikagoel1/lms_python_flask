from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import string
import random
import secrets
import datetime
from flask_mail import Mail, Message
from flask_migrate import Migrate
import os 

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Your SMTP server address
app.config['MAIL_PORT'] = 587  # Your SMTP server port
app.config['MAIL_USERNAME'] = 'your_username@example.com'  # Your SMTP username
app.config['MAIL_PASSWORD'] = 'your_password'  # Your SMTP password
app.config['MAIL_USE_TLS'] = True  # Enable TLS encryption
app.config['MAIL_USE_SSL'] = False  # Disable SSL encryption

# basedir = r"C:\Users\DGT IT\Desktop\Course_LMS"

mail = Mail(app)
app.secret_key = 'test'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#         'sqlite:///' + os.path.join(basedir, 'users.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

def send_reset_email(email, otp):
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'Hello,\n\nTo reset your password, please click on the following link:\n\n{url_for("reset_password", token=otp, _external=True)}\n\nIf you did not request this reset, please ignore this email.'
    mail.send(msg)

# Function to generate OTP
def generate_otp():
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(6))

# def generate_new_password(length=10):
#     characters = string.ascii_letters + string.digits + string.punctuation
#     new_password = ''.join(random.choice(characters) for _ in range(length))
#     return new_password

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email, password=password).first()
        
        if user:
            # Handle successful login
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        # Retrieve user data from database based on session['user_id']
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if user:
            # Pass user data to dashboard template
            return render_template('home.html', user=user)
        else:
            # Handle case where user_id is invalid or user doesn't exist
            return redirect(url_for('login'))
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
            # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return 'Email already exists!'

        # Create a new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('User registered successfully!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate OTP
            otp = generate_otp()
            
            # Save OTP in the database
            reset_entry = PasswordReset(user_id=user.id, otp=otp)
            db.session.add(reset_entry)
            db.session.commit()
            
            # Send email with reset link containing OTP
            send_reset_email(email, otp)
            
            flash('An email with instructions to reset your password has been sent to your email address.')
            return redirect(url_for('login'))
        else:
            flash('No user found with that email address.')
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_entry = PasswordReset.query.filter_by(otp=token).first()
    
    if not reset_entry:
        flash('Invalid or expired token.')
        return redirect(url_for('login'))
    
    # Check if token is within time limit (e.g., 15 minutes)
    if datetime.utcnow() - reset_entry.timestamp > timedelta(minutes=15):
        flash('Token expired. Please request a new password reset.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Update user's password in the database
        new_password = request.form['password']
        user = User.query.get(reset_entry.user_id)
        user.password = new_password
        db.session.delete(reset_entry)  # Delete reset entry from the database
        db.session.commit()
        
        flash('Your password has been reset successfully. You can now log in with your new password.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/calendar')
def calendar():
    # Logic to fetch active dates and to-do list can be added here
    return render_template('calendar.html')

@app.route('/placement_prep')
def placement_prep():
    return render_template('placement_prep.html')

@app.route('/start_interview')
def start_interview():
    return render_template('interview_form.html')

@app.route('/suggested_questions', methods=['POST'])
def suggested_questions():
    job_role = request.form['job_role']
    experience = request.form['experience']

    # Logic to determine suggested questions based on job role and experience
    # This could involve querying a database or using some predefined rules
    # For simplicity, let's assume some static questions
    suggested_questions = [
        "Tell me about yourself.",
        "Why do you want to work for our company?",
        "Describe a situation where you had to deal with a difficult coworker.",
        # Add more questions here
    ]

    return render_template('suggested_questions.html', questions=suggested_questions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
