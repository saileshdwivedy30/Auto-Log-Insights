import os
from flask import Flask, request, Response, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import jsonpickle
from elasticClient import ESClient

# Temporary folder for keeping uploads ( can remove later if we want to send it immediately.)
UPLOAD_FOLDER = 'uploads'

# Change the allowed extensions if needed
ALLOWED_EXTENSIONS = {'txt', 'csv',}

# Creating app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'team15'

es = ESClient()


@app.route("/", methods=["GET", "POST"])
def auth():
    mode = request.args.get('mode', 'login')  # Default mode is 'login'

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        esuser = es.check_user(username)
        if mode == 'register':  # Registration logic
            if not username or not password:
                flash('Username and password are required!', 'error')
                return redirect(url_for('auth', mode='register', show_message=True, msg = "Error: Username and password are required!" ))

            if esuser:
                flash('Username already exists!', 'error')
                return redirect(url_for('auth', mode='register'))

            # Hash and store the password
            es.registerUser(username,generate_password_hash(password))
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth', mode='login',show_message=True, msg="Registration successful! You can now log in."))

        elif mode == 'login':  # Login logic
            if not esuser or not check_password_hash(esuser[1], password):
                flash('Invalid username or password!', 'error')
                return redirect(url_for('auth', mode='login', show_message=True, msg="Error: Invalid username or password!"))

            flash(f'Welcome, {username}!', 'success')
            print("generated password", generate_password_hash(password))
            url = es.loginUser(username,generate_password_hash(password))
            session["kibana_url"] =url
            return redirect(url_for("home"))

    # Render the same template, passing the current mode
    return render_template('login.html', mode=mode)
    
@app.route('/home/')
def home():
    # Pass the Kibana URL to the template
    kibana_url=session['kibana_url']
    return render_template('home.html',kibana_url=kibana_url)

app.run(host="0.0.0.0", port=5000)
