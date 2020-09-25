from __future__ import print_function
import urllib.request
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
import numpy as np
import math
import cv2
import json
import requests
import sys
import aiohttp
import aiofiles
import hashlib
import asyncio
import os
import time
from hashlib import algorithms_available


async def get_online_person() -> bytes:
    url = "https://thispersondoesnotexist.com/image"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    }
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers) as r:
            return await r.read()


def create_collages(image_dir):
    image_path = os.listdir(image_dir)

    # Specify collage size.
    # TODO: Determine the size of a web page to determine collage size.
    collage_size = 6

    # Horizontally stacking images to create rows.
    rows = []
    k = 0  # counter for number of rows
    cur_row = cv2.imread(os.path.join(image_dir, image_path[0]))
    for i in range(collage_size**2):
        if i % collage_size == 0:
            if k > 0:
                # Finished with row, append this one and start new one.
                rows.append(cur_row)
                k = 0
            cur_row = cv2.imread(os.path.join(image_dir, image_path[i]))
            k += 1
        else:
            # Continue stacking images to horizontal row.
            cur_img = cv2.imread(os.path.join(image_dir, image_path[i]))
            cur_row = np.hstack([cur_row, cur_img])
            if (i == 35):
                rows.append(cur_row)

    collage = rows[-1]
    for i in range(len(rows)-1):
        collage = np.vstack([rows[i], collage])

    return collage


async def main():
    while True:
        # Get image from thispersondoesnotexist.com
        picture = await get_online_person()  # bytes representation of the image

        # Cascade files.
        face_cascade = cv2.CascadeClassifier(
            'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

        # Prep image.
        img = cv2.imread("a_beautiful_person.jpeg")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Iterate faces.
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            # img = cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 0)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                print("new eyes..")
                eyeimg = roi_color[ey:ey+eh, ex:ex+ew]
                # make it a 60 x 60 pixel image.
                eyeimg = cv2.resize(eyeimg, (60, 60))
                cv2.imwrite('./tmp/eyes_' + str(ew) + str(eh) + '.jpg', eyeimg)
                # cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 255, 255), 0)

        # Create a collage.
        collage = create_collages("./tmp/")

        # Remove old eye images when it reaches a certain length.
        eyedir = os.listdir("./tmp/")
        diramount = len(os.listdir("./tmp/"))
        if (diramount > 42):
            for i in range(diramount - 36):
                f = eyedir[diramount - 1 - i]
                os.remove("./tmp/" + f)

        addr = 'https://these-eyes-do-not-exist.herokuapp.com/'
        # addr = 'http://127.0.0.1:5000'

        server_url = addr + '/api/test'
        # prepare headers for http request
        content_type = 'image/jpg'
        headers = {'content-type': content_type}
        # encode image as jpeg
        _, img_encoded = cv2.imencode('.jpeg', collage)
        response = requests.post(
            server_url, data=img_encoded.tobytes(), headers=headers)

        time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
