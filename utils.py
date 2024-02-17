import segno
from flask import request


def gen_qrcode(current_user):
    url = str(request.environ.get('HTTP_ORIGIN')) +"/profile/" + str(current_user.pid)
    print(url)
    return segno.make(url)