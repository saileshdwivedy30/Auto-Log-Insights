import os
from flask import Flask, request, Response
from werkzeug.utils import secure_filename
import jsonpickle

# Temporary folder for keeping uploads ( can remove later if we want to send it immediately.)
UPLOAD_FOLDER = 'uploads'

# Change the allowed extensions if needed
ALLOWED_EXTENSIONS = {'txt', 'csv',}

# Creating app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create a temporary folder to keep uploaded log files if not already there.
if not os.path.exists(app.config['UPLOAD_FOLDER']):
       os.makedirs(app.config['UPLOAD_FOLDER'])

# check if the extension of the file is in allowed list
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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


app.run(host="0.0.0.0", port=5000)