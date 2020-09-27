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


def get_checksum_from_picture(picture: bytes, method: str = "md5") -> str:
    """Calculate the checksum of the provided picture, using the desired method.
    Available methods can be fetched using the the algorithms_available function.
    :param picture: picture as bytes
    :param method: hashing method as string (optional, default=md5)
    :return: checksum as string
    """
    h = hashlib.new(method.lower())
    h.update(picture)
    return h.hexdigest()


async def save_picture(picture: bytes, file: str = None) -> None:
    """Save a picture to a file.
    The picture must be provided as it content as bytes.
    The filename must be provided as a str with the absolute or relative path where to store it.
    If no filename is provided, a filename will be generated using the MD5 checksum of the picture, with jpeg extension.
    :param picture: picture content as bytes
    :param file: filename as string, relative or absolute path (optional)
    :return: None
    """
    if file is None:
        file = get_checksum_from_picture(picture) + ".jpeg"
    async with aiofiles.open(file, "wb") as f:
        await f.write(picture)


def create_collage(image_dir):
    image_path = os.listdir(image_dir)

    # Specify collage size.
    # TODO: Use the size of a web page to determine collage size.
    collage_size = 12

    # Horizontally stacking images to create rows.
    rows = []
    cur_row = cv2.imread(os.path.join(image_dir, image_path[0]))
    for i in range(1, collage_size**2):
        if i % collage_size == 0:
            # Finished with row, append this one and start new one.
            rows.append(cur_row)
            cur_row = cv2.imread(os.path.join(image_dir, image_path[i]))
        elif i == (collage_size**2)-1:
            # append last row.
            cur_img = cv2.imread(os.path.join(image_dir, image_path[i]))
            cur_row = np.hstack([cur_row, cur_img])
            rows.append(cur_row)
        else:
            # Continue stacking images to horizontal row.
            cur_img = cv2.imread(os.path.join(image_dir, image_path[i]))
            cur_row = np.hstack([cur_row, cur_img])

    # Append all horizontal rows vertically.
    collage = rows[0]
    for i in range(1, len(rows)):
        collage = np.vstack([rows[i], collage])

    return collage


async def main():
    while True:
        # Get image from thispersondoesnotexist.com
        picture = await get_online_person()  # bytes representation of the image
        await save_picture(picture, "a_beautiful_person.jpeg")

        # Cascade files.
        face_cascade = cv2.CascadeClassifier(
            'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

        # Prep image.
        # img = cv2.imread("a_beautiful_person.jpeg")
        img = cv2.imread("a_beautiful_person.jpeg")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Iterate faces.
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            img = cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 0)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                print("new eye..")
                eyeimg = roi_color[ey:ey+eh, ex:ex+ew]
                # make it a 60 x 60 pixel image.
                eyeimg = cv2.resize(eyeimg, (60, 60))
                cv2.imwrite('./tmp/eyes_' + str(ew) + str(eh) + '.jpg', eyeimg)
                # cv2.rectangle(roi_color, (ex, ey),
                #               (ex+ew, ey+eh), (255, 255, 255), 0)

        # Create a collage.
        collage = create_collage("./tmp/")

        # Remove old eye images when it reaches a certain length.
        eyedir = os.listdir("./tmp/")
        diramount = len(os.listdir("./tmp/"))
        maxfileamount = 144
        if (diramount > maxfileamount):
            for i in range(diramount - maxfileamount):
                print("deleting eye..")
                f = eyedir[diramount - 1 - i]
                os.remove("./tmp/" + f)

        addr = 'http://127.0.0.1:5000'

        server_url = addr + '/api/test'
        # prepare headers for http request
        content_type = 'image/jpg'
        headers = {'content-type': content_type}
        # encode image as jpeg
        _, img_encoded = cv2.imencode('.jpeg', collage)
        response = requests.post(
            server_url, data=img_encoded.tobytes(), headers=headers)

        time.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
