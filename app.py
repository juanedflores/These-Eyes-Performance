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
import base64
import numpy as np
import collections
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


@app.route('/api/detectEyes', methods=['POST'])
def post_eyeDetect():
    r = request
    # decode from base64
    im_bytes = base64.b64decode(r.data)
    # convert string of image data to uint8
    nparr = np.frombuffer(im_bytes, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Cascade files.
    face_cascade = cv2.CascadeClassifier(
        'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    # Prep image.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Iterate faces.
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    eyesdetected = 0
    eyelist = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            eyesdetected += 1
            print("new eye..")
            eyeimg = roi_color[ey:ey+eh, ex:ex+ew]
            # make it a 60 x 60 pixel image.
            eyeimg = cv2.resize(eyeimg, (60, 60))
            # cv2.imwrite('./face.jpg', eyeimg)
            _, im_arr = cv2.imencode('.jpg', eyeimg)
            im_bytes = im_arr.tobytes()
            im_b64 = base64.b64encode(im_bytes)
            eyelist.append(im_b64)
            eyeimg = cv2.rectangle(roi_color, (ex, ey),
                                   (ex+ew, ey+eh), (255, 0, 0), 5)
            # cv2.imwrite('./tmp/eyes_' + str(ew) + str(eh) + '.jpg', eyeimg)

    # Eyes = collections.namedtuple('Eyes', ['num', 'img'])
    # response = Eyes(str(eyesdetected), eyeimg)
    # eyesResponse = Eyes(str(eyesResponse), eyeimg)

    # img = cv2.imread('./face.jpg')
    # im_arr: image in Numpy one-dim array format.
    # _, im_arr = cv2.imencode('.jpg', img)
    # im_bytes = im_arr.tobytes()
    # im_b64 = base64.b64encode(im_bytes)

    print(eyesdetected)
    print(eyelist)
    d = dict()
    d['num'] = str(eyesdetected)
    d['img'] = str(eyelist)

    return d


@app.route('/api/insertEyes', methods=['POST'])
def post_eyeInsert():
    r = request
    # decode from base64
    im_bytes = base64.b64decode(r.data)
    # convert string of image data to uint8
    nparr = np.frombuffer(im_bytes, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Cascade files.
    face_cascade = cv2.CascadeClassifier(
        'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    # Prep image.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Iterate faces.
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    eyesdetected = 0
    eyelist = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            print("new eye..")
            eyeimg = cv2.rectangle(roi_color, (ex, ey),
                                   (ex+ew, ey+eh), (255, 0, 0), 5)
            eyeimg = roi_color[ey:ey+eh, ex:ex+ew]
            # make it a 60 x 60 pixel image.
            eyeimg = cv2.resize(eyeimg, (60, 60))
            cv2.imwrite('./tmp/eyes_' + str(ew) + str(eh) + '.jpg', eyeimg)

    d = dict()
    d['num'] = str(eyesdetected)
    d['img'] = str(eyelist)
    return d


if __name__ == "__main__":
    # app.run(extra_files=extra_dirs)
    app.run(debug=True)
