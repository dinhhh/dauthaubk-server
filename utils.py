from flask import Response, request
from bson.json_util import dumps


def convert_to_resp(data):
    resp = dumps({"data": data}, ensure_ascii=False)
    response = Response(resp, content_type="application/json; charset=utf-8")
    return response


def convert_to_resp_with_out_prefix(data):
    resp = dumps(data, ensure_ascii=False)
    response = Response(resp, content_type="application/json; charset=utf-8")
    return response


def get_page_and_size(request):
    page = request.args.get('page', default=0, type=int)
    size = request.args.get('size', default=5, type=int)
    return page, size

