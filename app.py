from datetime import datetime
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "upload.db"))

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)

class gambar(db.Model):
    id = db.Column(db.Integer, unique=True,primary_key=True)
    tanggal = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    filename = db.Column(db.String(200))
    path = db.Column(db.String(200))
db.create_all()

UPLOAD_FOLDER = 'image/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/upload', methods=['POST'])
def upload_file():

    if 'image' not in request.files:
        resp = jsonify({'msg': "No body image attached in request"})
        resp.status_code = 501
        return resp
 
    image = request.files['image']

    if image.filename == '':
        resp = jsonify({'msg': "No file image selected"})
        resp.status_code = 404
        return resp
     
    error = {}
    # success = False
         
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        success = True
    else:
        error[image.filename] = "File type is not allowed"
 
    if success and error:
        error['Message'] = "File not uploaded"
        resp = jsonify(error)
        resp.status_code = 500
        return resp
    if success:
        try:
            filename = secure_filename(image.filename)
            urlpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # print('ini path ',urlpath)

            data = gambar(filename = filename, path = urlpath)
            db.session.add(data)
            db.session.commit()
            
            resp = jsonify({'message' : 'File berhasil diunggah'})
            resp.status_code = 201
            return resp
        except Exception as e:
            resp = jsonify('errors')
            resp.status_code = 500
            return resp
 
if __name__ == '__main__':
    app.run(debug=True, port=8900)