import io
import requests
from PIL import Image
import re
import argparse
import sys

def post_latex_clean(string):
    """
    Post-processing of the latex sentences with step 1 removing the "\\" and step remove the weird ";"
    :param string: Latex string from the model
    :return: clear latex result
    """
    char = '\\\\'
    pattern = char + '{2,}'
    string = re.sub(pattern, char, string)
    string = string.replace("\\;","")
    string = string.replace("\\x", "\\\\x")

    return string

def img2latex(url,file, nx=200):
    """
    Send image thought restful API and reture the latex result
    :param url: restful API url
    :param file: image file
    :param nx: the target size after shrinking the picture
    :return: the model prediction
    """
    uploaded_file = file
    im = Image.open(uploaded_file)
    (x, y) = im.size
    ny = y * nx/x
    # shrink the image to smaller size for better prediction
    im_resize = im.convert("RGB").resize((int(nx),int(ny)))
    buf = io.BytesIO()
    im_resize.save(buf, format='JPEG')
    byte_im = buf.getvalue()
    r = requests.post(url, files={'file': byte_im})
    rs = post_latex_clean( r.text)
    return rs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default="../resources/images/SVIIvR/4.png")
    args = parser.parse_args()


    print(img2latex('http://100.26.10.46:8502/bytes/', args.path))