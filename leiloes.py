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
from datetime import datetime

import re
import logging
import psycopg2
import time
from aux import encode_password, verify_email, generate_token_value

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


##
# Demo GET
##
# Obtain all departments, in JSON format
##
# To use it, access:
##
# http://localhost:8080/departments/
##

@app.route("/departments/", methods=['GET'], strict_slashes=True)
def get_all_departments():
    logger.info("###              DEMO: GET /departments              ###")

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT ndep, nome, local FROM dep")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- departments  ----")
    for row in rows:
        logger.debug(row)
        content = {'ndep': int(row[0]), 'nome': row[1], 'localidade': row[2]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)


##
# Demo GET
##
# Obtain department with ndep <ndep>
##
# To use it, access:
##
# http://localhost:8080/departments/10
##

@app.route("/departments/<ndep>", methods=['GET'])
def get_department(ndep):
    logger.info(
        "###              DEMO: GET /departments/<ndep>              ###")

    # logger.debug(f"ndep: {ndep}')

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT ndep, nome, local FROM dep where ndep = %s", (ndep,))
    rows = cur.fetchall()

    row = rows[0]

    logger.debug("---- selected department  ----")
    logger.debug(row)
    content = {'ndep': int(row[0]), 'nome': row[1], 'localidade': row[2]}

    conn.close()
    return jsonify(content)



###################################
#### FUNÇÃO que cria um token #####
###################################

def add_token(user_name,user_email):
    logger.info("### New token created ###")

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New Token ----")

    hours = 1
    hours_added = datetime. timedelta(hours = hours)
    token_validade = datetime. now() + hours_added

    token_value = generate_token_value(base_token_value)

    
    statement = """
                  INSERT INTO token (valor, validade, utilizador_user_name, utilizador_email) 
                          VALUES (%s, %s, %s, %s)"""

    values = (token_value, token_validade,
              user_name,user_email)

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Token created with success!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Token could not be created.'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)



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

    add_token(payload["user_name"], payload["email"])

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

    """
    if verify_password(payload["password"]) == False:
        result = "Error: Wrong password"
        logger.error(result)
        if conn is not None:
            conn.close()
           
    else:
    """
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Admin inserted with success!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Admin was not inserted.'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


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

##
# Demo PUT
##
# Update a department based on the a JSON payload
##
# To use it, you need to use postman or curl:
##
# curl -X PUT http://localhost:8080/departments/ -H "Content-Type: application/json" -d '{"ndep": 69, "localidade": "Porto"}'
##


@app.route("/departments/", methods=['PUT'])
def update_departments():
    logger.info("###              DEMO: PUT /departments              ###")
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    # if content["ndep"] is None or content["nome"] is None :
    #    return 'ndep and nome are required to update'

    if "ndep" not in content or "localidade" not in content:
        return 'ndep and localidade are required to update'

    logger.info("---- update department  ----")
    logger.info(f'content: {content}')

    # parameterized queries, good for security and performance
    statement = """
                UPDATE dep 
                  SET local = %s
                WHERE ndep = %s"""

    values = (content["localidade"], content["ndep"])

    try:
        res = cur.execute(statement, values)
        result = f'Updated: {cur.rowcount}'
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
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
    #variables
    base_token_value = 1_000_000_000

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
