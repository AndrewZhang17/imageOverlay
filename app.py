import os
from flask import Flask, request, render_template, send_from_directory
import cv2

app = Flask(__name__)

HTML_TEMPLATE = "upload_image.html"
BACKGROUND_IMAGE_NAME = "background.png"
OVERLAY_IMAGE_NAME = "overlay.png"
RESULT_IMAGE_NAME = "result.png"

overlay = cv2.imread(OVERLAY_IMAGE_NAME, cv2.IMREAD_UNCHANGED)

def addOverlay(background, foreground):
    foreground = cv2.resize(foreground, (background.shape[0], background.shape[1]))

    # normalize alpha channels from 0-255 to 0-1
    if len(background[0,0]) == 3:
        background = cv2.cvtColor(background, cv2.COLOR_RGB2RGBA)
    alpha_background = background[:,:,3] / 255.0
    alpha_foreground = foreground[:,:,3] / 255.0

    # set adjusted colors
    for color in range(0, 3):
        background[:,:,color] = alpha_foreground * foreground[:,:,color] + \
            alpha_background * background[:,:,color] * (1 - alpha_foreground)

    # set adjusted alpha and denormalize back to 0-255
    background[:,:,3] = (1 - (1 - alpha_foreground) * (1 - alpha_background)) * 255

    return background

@app.route("/", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            if image:
                image.save(BACKGROUND_IMAGE_NAME)

                img = cv2.imread(BACKGROUND_IMAGE_NAME, cv2.IMREAD_UNCHANGED)
                result = addOverlay(img, overlay)
                cv2.imwrite(RESULT_IMAGE_NAME, result)

                return render_template(HTML_TEMPLATE, uploaded_image=RESULT_IMAGE_NAME)
    return render_template(HTML_TEMPLATE)

@app.route("/uploads/<filename>")
def send_uploaded_file(filename=""):
    return send_from_directory(".", filename)