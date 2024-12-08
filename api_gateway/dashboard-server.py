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
app.secret_key = 'randomkey'

# Create a temporary folder to keep uploaded log files if not already there.
if not os.path.exists(app.config['UPLOAD_FOLDER']):
       os.makedirs(app.config['UPLOAD_FOLDER'])

# check if the extension of the file is in allowed list
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

es = ESClient()
users_db = {
    user
}

@app.route('/apiv1/generate-insight', methods=['POST'])
def processLog():

    response = {}
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            response={"msg": "Error: 'No files in request"}
            status=400
        
        file = request.files['file']

        # if an empty? file exists ( not sure how that will be)
        if file.filename == '':
            response={"msg": "Error: 'Invalid File"}
            status=400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('download_file', name=filename))
            response = {"msg":"Success! file received successfully"}
            status=200
        # either file does not exist or is not the extension allowed.
        else:
            response={"msg": "Error: 'Invalid File"}
            status=400


    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=status, mimetype="application/json")

@app.route("/", methods=["GET", "POST"])
def auth():
    mode = request.args.get('mode', 'login')  # Default mode is 'login'

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if mode == 'register':  # Registration logic
            if not username or not password:
                flash('Username and password are required!', 'error')
                return redirect(url_for('auth', mode='register', show_message=True, msg = "Error: Username and password are required!" ))

            if username in users_db:
                flash('Username already exists!', 'error')
                return redirect(url_for('auth', mode='register'))

            # Hash and store the password
            users_db[username] = generate_password_hash(password)
            es.registerUser(username,password)
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth', mode='login',show_message=True, msg="Registration successful! You can now log in."))

        elif mode == 'login':  # Login logic
            if username not in users_db or not check_password_hash(users_db[username], password):
                flash('Invalid username or password!', 'error')
                return redirect(url_for('auth', mode='login', show_message=True, msg="Error: Invalid username or password!"))

            flash(f'Welcome, {username}!', 'success')
            es.loginUser()
            return redirect(url_for('home'))

    # Render the same template, passing the current mode
    return render_template('login.html', mode=mode)
    
# Kibana dashboard URL
KIBANA_BASE_URL = "http://localhost:5601"
KIBANA_DISCOVER_BASE_URL = "http://localhost:5601/app/discover#/"
# index = 
KIBANA_FILTERS= "?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-30d,to:now))&_a=(columns:!(message),filters:!(),index:'user1-logs',interval:auto,query:(language:kuery,query:''),sort:!())"

KIBANA_FINAL_URL = KIBANA_DISCOVER_BASE_URL+KIBANA_FILTERS
@app.route('/home')
def home():
    # Pass the Kibana URL to the template
    return render_template('home.html', kibana_url=KIBANA_FINAL_URL)

app.run(host="0.0.0.0", port=5000)

