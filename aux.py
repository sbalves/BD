from flask import Flask, jsonify, request
from datetime import datetime

import re
import logging
import psycopg2
import time

base = 1_000_000_000


def encode(obj):
    return hash(obj)


password_hash = encode("pato345")
print("pass codificada: " + str(password_hash))


def verify_password(user_pass):
    return hash(user_pass) == password_hash


def verify_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

    if(re.search(regex, email)):
        print("Valid Email")
        return True

    else:
        print("Invalid Email")
        return False


def generate_token_value():
    global base
    return base + 1


"""
def decode(value):
    return # Como eu decodificaria aqui ?

password_hash = encode("pato345")
password = decode(password_hash)
"""
