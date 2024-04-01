from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_migrate import Migrate


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

# Configure default database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_BINDS'] = { 'user': 'sqlite:///user.db', 'todo' : 'sqlite:///todo.db'}
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#         'sqlite:///' + os.path.join(basedir, 'users.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)