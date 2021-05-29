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
# Autores:
# Eva Texeira
# Joana Antunes
# Sofia Alves
## University of Coimbra


from flask import Flask, jsonify, request
from datetime import datetime, timedelta

import re
import logging
import psycopg2
import time
import os
from _aux import verify_password, verify_email

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

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New Token ----")

    hours = 1
    hours_added = timedelta(hours = hours)
    token_validade = datetime.now() + hours_added

    add_token.counter += 1
    token_value = add_token.counter

    logger.debug(f'token_value: {token_value}')
    statement = """
                INSERT INTO token (valor, validade, utilizador_user_name) 
                VALUES (%s, %s, %s)
                """

    values = (token_value, token_validade, user_name)

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Token was successfully created.'
        logger.info(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Token could not be created.'
    finally:
        if conn is not None:
            conn.close()
    return token_value


# Add a new user
@app.route("/dbproj/user/", methods = ['POST'])
def add_users():
    logger.info("### POST - Add new user ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New User ----")
    logger.debug(f'payload: {payload}')

    statement = """
                INSERT INTO utilizador (user_name, email, password, estado, avaliacao, admin) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """

    values = (payload["user_name"], payload["email"], payload["password"], "true", "0", "false")

    if verify_email(payload["email"]) == False:
        result = "Invalid email."
        logger.error(result)
        if conn is not None:
            conn.close()
    else:
        try:
            cur.execute(statement, values)
            cur.execute("commit")
            result = 'User inserted with success!'
            logger.info(result)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = 'User was not inserted.'
        finally:
            if conn is not None:
                conn.close()
    return jsonify(result)


# Add new admin
@app.route("/dbproj/admin/", methods = ['POST'])
def add_admin():
    logger.info("### POST - Add new admin ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if payload["user_name"] is None or payload["email"] is None or payload["password"]:
        return 'Username, email and password are required to register.'

    logger.info("---- New Admin ----")
    logger.debug(f'payload: {payload}')

    statement = """
                INSERT INTO utilizador (user_name, email, password, estado, avaliacao, admin) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """

    values = (payload["user_name"], payload["email"], payload["password"], "true", "0", "true")

    if verify_password(payload["password"]) == False:
        result = "Wrong password!"
        logger.error(result)
        if conn is not None:
            conn.close()
    else:
        try:
            cur.execute(statement, values)
            cur.execute("commit")
            result = 'Admin was inserted!'
            logger.info(result)
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

@app.route("/dbproj/user/", methods = ['PUT'])
def user_autentification():
    logger.info("### PUT - Login user/admin ###")
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if "user_name" not in content or "password" not in content:
        return 'Username and password are required to autenticate!'

    logger.info("----  Autenticate User/Admin  ----")
    logger.debug(f'content: {content}')

    find_user = """
                SELECT user_name, password 
                FROM utilizador
                WHERE user_name = %s and password = %s
                """
    """
    verify_token = """ """
                   SELECT valor
                   FROM token
                   WHERE utilizador_user_name = %s
                   """
    """
    """

    values1 = (content["user_name"], content["password"])
    # values2 = (content["user_name"])

    try:
        cur.execute(find_user, values1)
        row1 = cur.fetchone()

        if row1 == None:
            result = 'Username or password invalid.'
            logger.error(result)
        else:
            """
            cur.execute(verify_token, values2)
            row2 = cur.fetchone()

            if row2 == None:
                result = 'Token does not exist yet. Creating new token...'
                logger.info(result)
            """
            token_value = add_token(row1[0])
            result = f'Login confirmed! Token value: {token_value}'
            logger.info(result)
            """
            else:
                t1 = datetime.strptime(row2[1], "%b %d %H:%M:%S %Y")
                if datetime.now().hour > t1.hour:
                    result = 'Token still valid.'
                    logger.inf(result)
                else:
                    token_value = add_token(row[0])
                    result = f'Login confirmed! Token value: {token_value}'
                    logger.info(result)
            """
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'The login failed.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


# Criação de um novo leilão
@app.route("/dbproj/leilao/", methods = ['POST'])
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

    values = (payload["titulo"], payload["ean_artigo"], "1", payload["data_final"], datetime.now(), payload["preco_min"], "false")

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


# Listar leilões
@app.route("/dbproj/leiloes/", methods = ['GET'])
def list_auctions():
    logger.info("### GET - List Auctions ###")
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if content is not None:
        result = 'To list auctions there is no need of request.'
        logger.error(result)
        return result

    list_auctions = """
                    SELECT titulo, descricao
                    FROM leilao, descricao
                    WHERE leilao.ean_artigo = descricao.ean_artigo
                    """

    try:
        cur.execute(list_auctions)
        rows = cur.fetchall()

        lista = []
        logger.info("----  List Auctions  ----")
        for row in rows:
            logger.debug(row)
            content = {'Título': row[0], 'Descrição': row[1]}
            lista.append(content)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'User was not inserted.'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(lista)



##########################################################
# DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(user="postgres",
                          password="postgres",
                          host="localhost",
                          port="5432",
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
