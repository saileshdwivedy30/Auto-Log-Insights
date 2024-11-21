import os
from flask import Flask, request, Response
from werkzeug.utils import secure_filename
import jsonpickle

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv',}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
       os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/apiv1/generate-insight', methods=['POST'])
def processLog():
    # data = request.get_json()
    # hash = mc.addmp3Tobucket(mc.ipbucket,data['mp3'])
    # rc.enqueueWork(item=hash)
    
    response = {}
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            response={"msg": "Error: 'No files in request"}
            status=400
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        if file.filename == '':
            response={"msg": "Error: 'Invalid File"}
            status=400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('download_file', name=filename))
            response = {"msg":"Success! file received successfully"}
            status=200

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=status, mimetype="application/json")


app.run(host="0.0.0.0", port=5000)