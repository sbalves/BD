##
# =============================================
# ============== Bases de Dados ===============
# ============== LEI  2020/2021 ===============
# =============================================
# ============== Projeto Final ================
# =============================================
# =============================================
# === Department of Informatics Engineering ===
# =========== University of Coimbra ===========
# =============================================
##
# Authors:
# Eva Texeira
# Joana Antunes
# Sofia Alves
# University of Coimbra


from flask import Flask, jsonify, request
from datetime import datetime, timedelta

import re
import logging
import psycopg2
import time
import os
from aux import verify_password, verify_email

app = Flask(__name__)


@app.route('/')
def hello():
    return """

    Hello World!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2021 Team<br/>
    <br/>
    """


###################################
#### FUNÇÃO que cria um token #####
###################################

def add_token(user_name):
    logger.info("### New token created ###")

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New Token ----")

    hours = 1
    hours_added = timedelta(hours=hours)
    token_validade = datetime.now() + hours_added

    add_token.counter += 1
    token_value = add_token.counter

    statement = """
                  INSERT INTO token (valor, validade, utilizador_user_name) 
                          VALUES (%s, %s, %s)"""

    values = (token_value, token_validade,
              user_name)

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Token created with success!'
        logger.info(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Token could not be created.'
    finally:
        if conn is not None:
            conn.close()
    return token_value


# Add a new user
@app.route("/dbproj/user/", methods=['POST'])
def add_users():
    logger.info("### POST - Add new user ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New User ----")
    logger.debug(f'payload: {payload}')

    statement = """
                INSERT INTO utilizador (user_name, email, password, estado, avaliacao, admin) 
                VALUES (%s, %s, %s, %s, %s, %s)"""

    values = (payload["user_name"], payload["email"],
              payload["password"], "true", "0", "false")

    if verify_email(payload["email"]) == False:
        result = "Error: Invalid email"
        logger.error(result)
        if conn is not None:
            conn.close()
    else:
        try:
            cur.execute(statement, values)
            cur.execute("commit")
            result = 'User inserted with success!'
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = 'User was not inserted.'
        finally:
            if conn is not None:
                conn.close()
    return jsonify(result)


# Add new admin
@app.route("/dbproj/admin/", methods=['POST'])
def add_admin():
    logger.info("### POST - Add new admin ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New Admin ----")
    logger.debug(f'payload: {payload}')

    statement = """
                INSERT INTO utilizador (user_name, email, password, estado, avaliacao, admin) 
                VALUES (%s, %s, %s, %s, %s, %s)"""

    values = (payload["user_name"], payload["email"],
              payload["password"], "true", "0", "true")

    if verify_password(payload["password"]) == False:
        result = "Error: Wrong password"
        logger.error(result)
        if conn is not None:
            conn.close()
    else:
        try:
            cur.execute(statement, values)
            cur.execute("commit")
            result = 'Admin was inserted!'
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = 'Admin was not inserted.'
        finally:
            if conn is not None:
                conn.close()
    return jsonify(result)


###################################
#### FUNÇÃO de autenticação #######
###################################

@app.route("/dbproj/user/", methods=['PUT'])
def user_autentification():
    logger.info("### PUT - Login user ###")
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if content["user_name"] is None or content["password"] is None:
        return 'Username and password are required to login.'

    if "user_name" not in content or "password" not in content:
        return 'User_name and password are required to autenticate!'

    logger.info("----  Autenticate User  ----")
    logger.info(f'content: {content}')

    find_user = """
                SELECT user_name, password 
                FROM utilizador
                WHERE user_name = %s and password = %s"""

    verify_token = """ 
                SELECT token.valor
                FROM token
                WHERE utilizador_user_name like %s"""

    values = (content["user_name"], content["password"])

    try:
        cur.execute(find_user, values)
        row = cur.fetchone()
        if row == None:
            result = 'Username or password invalid'
            logger.error(result)
        else:
            token_value = add_token(row[0])
            logger.info(row)
            result = f'Login confirmed! Token value: {token_value}'
    except (Exception, psycopg2.DatabaseError) as error:  # psycopg2
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)  # flask


@app.route("/dbproj/leilao/", methods=['POST'])
def new_auction():
    logger.info("### POST - Add new auction ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New auction ----")
    logger.debug(f'payload: {payload}')

    data_inicial = datetime.now()

    statement = """
                  INSERT INTO leilao (titulo, ean_artigo, estado, data_final, data_inicial, preco_min, utilizador_user_name, utilizador_email) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

    values = (payload["titulo"], payload["ean_artigo"], "1",
              payload["data_final"], data_inicial, payload["preco_min"], "false")

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'User inserted with success!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'User was not inserted.'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


##########################################################
# DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(user="postgres",
                          password="postgres",
                          host="localhost",
                          port="5432",  # mudei a porta- anterior: 5432
                          database="BD_Projeto")
    return db


##########################################################
# MAIN
##########################################################
if __name__ == "__main__":
    # variables
    add_token.counter = 1_000_000_009

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                                  '%H:%M:%S')
    # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    time.sleep(1)  # just to let the DB start before this print :-)

    logger.info("\n---------------------------------------------------------------\n" +
                "API v1.0 online: http://localhost:8080/departments/\n\n")

    app.run(host="localhost", port=8080,  debug=True, threaded=True)
