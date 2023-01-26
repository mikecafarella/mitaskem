import io
import requests
from PIL import Image
import re
def replace(string, char):
    pattern = char + '{2,}'
    string = re.sub(pattern, char, string)
    return string

def img2latex(url,file):
    uploaded_file = file
    im = Image.open(uploaded_file)
    (x, y) = im.size
    nx = 200
    ny = y*200/x
    # im_resize = im.convert("RGB")
    im_resize = im.resize((int(nx),int(ny)))
    buf = io.BytesIO()
    im_resize.save(buf, format='JPEG')
    byte_im = buf.getvalue()
    r = requests.post(url, files={'file': byte_im})
    rs = replace( r.text, '\\\\')
    return rs


if __name__ == "__main__":
    print(img2latex('http://127.0.0.1:8502/bytes/', '/Users/chunwei/Downloads/3.jpg'))