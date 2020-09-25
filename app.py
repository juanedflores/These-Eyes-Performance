import urllib.request
import os
from flask import Flask
from flask import send_file
from flask import render_template
from flask import request, Response
from flask import make_response
from flask import jsonify
from flask_cors import CORS, cross_origin
import jsonpickle
import cv2
import numpy as np
# from flask import request
# from flask import url_for
# from flask import redirect
PEOPLE_FOLDER = os.path.join('static', 'people_photo')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

extra_dirs = ['./static/people_photo/test.jpg']
extra_files = extra_dirs[:]



cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/image")
def get_Image():
    # url = "https://thispersondoesnotexist.com/image"
    # req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # with open("./static/people_photo/test.jpg", "wb") as f:
    # with urllib.request.urlopen(req) as r:
    # f.write(r.read())

    return send_file("./static/people_photo/test.jpg", mimetype='image/jpeg')


@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
@cross_origin()
def get_Home():

    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'test.jpg')
    return render_template("index.html", result=full_filename)


@app.route("/api/test", methods=['GET', 'POST'])
@cross_origin()
def get_Test():
    r = request
    # convert string of image data to uint8
    nparr = np.frombuffer(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # build a response dict to send back to client
    response = {'message': 'image received. size={}x{}'.format(
        img.shape[1], img.shape[0])}

    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    cv2.imwrite("./static/people_photo/test.jpg", img)

    # return send_file(response_pickled, mimetype='image/jpeg')
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'test.jpg')
    return render_template("index.html", result="test.jpg")
    # return make_response(response_pickled, 200)


if __name__ == "__main__":
    app.run(extra_files=extra_dirs)
