import json

import requests


def app(environ, start_response):
    if environ.get("REQUEST_METHOD") != "GET":
        status = "405 Method Not Allowed"
        body = ""
        response_headers = [
            ("Allow", "GET"),
        ]

    else:
        uri = environ.get("RAW_URI")[1:]
        if not uri or "/" in uri:
            status = "404 Not Found"
            body = "Page not found!"
            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(body))),
            ]
        else:
            try:
                response_from_api = get_course(uri)
                status = "200 OK"
            except requests.exceptions.ConnectTimeout as e:
                response_from_api = {
                    "Timeout error": "Failed to process request in time"
                }
                status = "408 Request Timeout"
            body = json.dumps(response_from_api)

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(body))),
            ]

    start_response(status, response_headers)
    return iter([body.encode()])


def get_course(currency: str):
    resource = f"https://api.exchangerate-api.com/v4/latest/{currency}"
    response = requests.get(resource, timeout=5)

    return response.json()
