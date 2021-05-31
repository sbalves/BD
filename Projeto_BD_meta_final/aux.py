from flask import Flask, jsonify, request
from datetime import datetime

import re
import logging
import psycopg2
import time


def encode(obj):
    return hash(obj)


password_hash = encode("pato345")
print("pass codificada: " + str(password_hash))


def verify_password(user_pass):
    return hash(user_pass) == password_hash


def verify_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        return True
    else:
        return False
