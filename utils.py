import segno
from flask import request


def gen_qrcode(current_user):
    url = "http://" + str(request.environ.get('HTTP_HOST') or '127.0.0.1:5000') +"/profile/" + str(current_user.pid)
    print(url)
    return segno.make(url)