import http.client

from flask import Flask

from app import util
from app.calc import Calculator

CALCULATOR = Calculator()
api_application = Flask(__name__)
HEADERS = {"Content-Type": "text/plain", "Access-Control-Allow-Origin": "*"}


@api_application.route("/")
def hello():
    return "Hello from The Calculator!\n"


@api_application.route("/calc/add/<op_1>/<op_2>", methods=["GET"])
def add(op_1, op_2):
    try:
        num_1, num_2 = util.convert_to_number(op_1), util.convert_to_number(op_2)
        return ("{}".format(CALCULATOR.add(num_1, num_2)), http.client.OK, HEADERS)
    except TypeError as e:
        return (str(e), http.client.BAD_REQUEST, HEADERS)


@api_application.route("/calc/substract/<op_1>/<op_2>", methods=["GET"])
def substract(op_1, op_2):
    try:
        num_1, num_2 = util.convert_to_number(op_1), util.convert_to_number(op_2)
        return ("{}".format(CALCULATOR.substract(num_1, num_2)), http.client.OK, HEADERS)
    except TypeError as e:
        return (str(e), http.client.BAD_REQUEST, HEADERS)


@api_application.route("/calc/multiply/<op_1>/<op_2>", methods=["GET"])
def multiply(op_1, op_2):
    try:
        num_1, num_2 = util.convert_to_number(op_1), util.convert_to_number(op_2)
        result = CALCULATOR.multiply(num_1, num_2)
        return ("{}".format(result), http.client.OK, HEADERS)
    except TypeError as e:
        return (str(e), http.client.BAD_REQUEST, HEADERS)


@api_application.route("/calc/divide/<op_1>/<op_2>", methods=["GET"])
def divide(op_1, op_2):
    try:
        num_1 = util.convert_to_number(op_1)
        num_2 = util.convert_to_number(op_2)

        if num_1 == 0 or num_2 == 0:
            # Requisito: responder 406 "NOT_ACCEPTABLE" en división por cero
            return ("Division by zero not allowed", http.client.NOT_ACCEPTABLE, HEADERS)

        result = CALCULATOR.divide(num_1, num_2)

        try:
            f = float(result)
            body = str(int(f)) if f.is_integer() else str(f)
        except Exception:
            body = str(result)

        return (body, http.client.OK, HEADERS)

    except ZeroDivisionError:
        return ("Division by zero not allowed", http.client.NOT_ACCEPTABLE, HEADERS)

    except TypeError as e:
        return (str(e), http.client.BAD_REQUEST, HEADERS)
        
