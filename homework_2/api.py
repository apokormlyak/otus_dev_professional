#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class BaseField:
    def __init__(self, value, required=False, nullable=True, max_val=None):
        self.value = value
        self.max_val = max_val
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        return (((value is None and not self.required) or (value is not None))
                and ((value is 'null' and self.nullable) or (value is not 'null'))
                and self._max_val_validate(value))

    def _max_val_validate(self, value):
        return (self.max_val is None) or (value <= self.max_val)


class Meta(type):
    def __new__(self, name, bases, namespace):
        fields = {
            name: field
            for name, field in namespace.items()
            if isinstance(field, BaseField)
        }
        new_namespace = namespace.copy()

        for name in fields.keys():
            del new_namespace[name]

        new_namespace['_fields'] = fields
        obj = super().__new__(self, name, bases, new_namespace)
        return obj


class CharField(BaseField):
    __metaclass__ = Meta

    def __init__(self, value=None, required=False, nullable=True, max_len=None):
        super().__init__(value, required=required, nullable=nullable, max_val=max_len)

    def validate(self, value):
        return super().validate(value)


class ArgumentsField(BaseField):
    __metaclass__ = Meta

    def __init__(self, value, required=True, nullable=True, max_len=None):
        super().__init__(value, required=required, nullable=nullable, max_val=max_len)

    def validate(self, value):
        if super().validate(value):
            ...
        else:
            return False


class EmailField(CharField):
    __metaclass__ = Meta

    def __init__(self, value=None, required=False, nullable=True, max_len=None):
        super().__init__(value, required=required, nullable=nullable, max_len=max_len)

    def validate(self, value):
        if super().validate(value):
            if not isinstance(value, str):
                return False
            else:
                return bool(str(value).find('@'))
        else:
            return False


class PhoneField(BaseField):
    __metaclass__ = Meta

    def __init__(self, value=None, required=False, nullable=True, max_len=None):
        super().__init__(value, required=required, nullable=nullable, max_val=max_len)
        self.len_number = 11

    def validate(self, value):
        if super().validate(value):
            if not isinstance(value, str) or not isinstance(value, int):
                return False
            else:
                return (len(str(value)) == self.len_number) and (str(value).startswith('7'))
        else:
            return False


class DateField(BaseField):
    __metaclass__ = Meta

    def __init__(self, value=None, required=False, nullable=True, max_len=None):
        super().__init__(value, required=required, nullable=nullable, max_val=max_len)

    def validate(self, value):
        if super().validate(value):
            if not isinstance(value, datetime.datetime):
                return False
            else:
                return value == datetime.datetime.strptime(str(value), '%d.%M.%Y')
        else:
            return False


class BirthDayField(DateField):
    __metaclass__ = Meta

    def __init__(self, value=None, required=False, nullable=True, max_len=None):
        super().__init__(value, required=required, nullable=nullable, max_len=max_len)

    def validate(self, value):
        if super().validate(value):
            return False
        else:
            return ((datetime.datetime.strptime(value, '%d.%M.%Y') -
                     datetime.datetime.now()).total_seconds() <=
                    (datetime.timedelta(days=365 * 70).total_seconds()))


class GenderField(BaseField):
    __metaclass__ = Meta

    def __init__(self, value=UNKNOWN, required=False, nullable=True, max_len=None):
        super().__init__(value, required=required, nullable=nullable, max_val=max_len)

    def validate(self, value):
        if super().validate(value):
            return value in (UNKNOWN, MALE, FEMALE)
        else:
            return False


class ClientIDsField(BaseField):
    __metaclass__ = Meta

    def __init__(self, value=0, required=True, nullable=False, max_len=None):
        super().__init__(value, required=required, nullable=nullable, max_val=max_len)
        self.value = []

    def validate(self, value):
        if super().validate(value):
            if not isinstance(value, list):
                return False
            else:
                for el in value:
                    if not isinstance(el, int):
                        return False
                return True
        else:
            return False


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(object):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(object):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = None, None
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
