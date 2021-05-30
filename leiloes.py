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
# University of Coimbra


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
    # seconds = 5
    hours_added = timedelta(hours=hours)
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


# Adiciona novo utilizador

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
                VALUES (%s, %s, %s, %s, %s, %s)
                """

    values = (payload["user_name"], payload["email"],
              payload["password"], "true", "0", "false")

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


# Adiciona novo administrador

@app.route("/dbproj/admin/", methods=['POST'])
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

    values = (payload["user_name"], payload["email"],
              payload["password"], "true", "0", "true")

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

@app.route("/dbproj/user/", methods=['PUT'])
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

    values1 = (content["user_name"], content["password"])

    try:
        cur.execute(find_user, values1)
        row1 = cur.fetchone()

        if row1 is None:
            result = 'Username or password invalid.'
            logger.error(result)
        else:
            token_value = add_token(row1[0])
            result = f'Login confirmed! Token value: {token_value}'
            logger.info(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'The login failed.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


####################################
#### Criação de um novo leilão #####
####################################

def delete_token(valor_token):
    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM token WHERE valor = %s", [valor_token])
        cur.execute("commit")
        result = "Token deleted with success"
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Description was not inserted.'
    finally:
        if conn is not None:
            conn.close()
    logger.info(result)


# Criacao de uma descrição
def add_description(descricao, ean_artigo):
    conn = db_connection()
    cur = conn.cursor()

    statement = """
                INSERT INTO descricao (descricao, data, leilao_ean_artigo)
                VALUES (%s, %s, %s)
                """

    values = (descricao, datetime.now(), int(ean_artigo))

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Description inserted with success!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Description was not inserted.'
    finally:
        if conn is not None:
            conn.close()
    return result


# Criacao de um leilao
def create_auction(payload, user_name):
    conn = db_connection()
    cur = conn.cursor()

    logger.info(payload)

    if "valor_token" not in payload or "titulo" not in payload or "ean_artigo" not in payload or "data_final" not in payload or "preco_min" not in payload or "descricao" not in payload:
        logger.info("entrou")
        return 'Username and password are required to autenticate!'

    statement = """
                INSERT INTO leilao (titulo, ean_artigo, estado, data_final, data_inicial, preco_min, utilizador_user_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

    values = (payload["titulo"], payload["ean_artigo"], "1",
              payload["data_final"], datetime.now(), payload["preco_min"], user_name)

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        add_description(payload["descricao"], payload["ean_artigo"])
        result = 'Auction created with success!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Auction was not created.'
    finally:
        if conn is not None:
            conn.close()
    logger.info(result)


@app.route("/dbproj/leilao/", methods=['POST'])
def new_auction():
    logger.info("### POST - Add new auction ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New auction ----")
    logger.debug(f'payload: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                result = "Auction was created."
                logger.info(f"row: {row}")
                create_auction(payload, row[2])
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Auction was not created.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


###################################
######## Listar leilões ###########
###################################


# Listar leilões
def list_all_auctions():
    conn = db_connection()
    cur = conn.cursor()

    list_auctions = """
                    SELECT titulo, descricao
                    FROM leilao, descricao
                    WHERE leilao.ean_artigo = descricao.leilao_ean_artigo and estado = 1
                    """

    try:
        cur.execute(list_auctions)
        rows = cur.fetchall()
        logger.info(rows)
        result = []
        logger.info("----  List Auctions  ----")
        for row in rows:
            logger.debug(row)
            content = {'Título': row[0], 'Descrição': row[1]}
            result.append(content)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not list all auctions.'
    finally:
        if conn is not None:
            conn.close()
    return result


@ app.route("/dbproj/leiloes/", methods=['GET'])
def list_auctions():
    logger.info("### GET - List Auctions ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- List Auctions ----")
    logger.debug(f'payload: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                result = list_all_auctions()
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Auctions could not be listed.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


###################################
###### Pesquisar leilões ##########
###################################

def list_searched_auctions(payload):
    conn = db_connection()
    cur = conn.cursor()

    if "ean_artigo" in payload.keys():
        list_auctions = """
                        SELECT titulo, descricao
                        FROM leilao, descricao
                        WHERE leilao.ean_artigo = %s and leilao.ean_artigo = descricao.leilao_ean_artigo  and estado = 1
                        """
        value = [payload["ean_artigo"]]

    elif "descricao" in payload.keys():
        list_auctions = """
                        SELECT titulo, descricao
                        FROM leilao, descricao
                        WHERE leilao.ean_artigo = descricao.leilao_ean_artigo and estado = 1 and descricao = %s
                        """
        value = [payload["descricao"]]

    else:
        result = 'Ean or description are required to search for an auction.'
        logger.error(result)
        return result

    try:
        cur.execute(list_auctions, value)
        rows = cur.fetchall()
        if len(rows) == 0:
            result = 'There are no auctions with such attributes.'
            logger.error(result)
        else:
            logger.info(rows)
            result = []
            logger.info("----  List Auctions  ----")
            for row in rows:
                logger.debug(row)
                content = {'Título': row[0], 'Descrição': row[1]}
                result.append(content)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not list all auctions.'
    finally:
        if conn is not None:
            conn.close()
    return result


@ app.route('/dbproj/leiloes/<keyword>/', methods=['GET'])
def search_auction(keyword):
    logger.info("### GET - List Auctions (by ID or description) ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- Search Auctions ----")
    logger.debug(f'payload: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                result = list_searched_auctions(payload)
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Auctions were not listed.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


################################################
####### Consultar detalhes dos leilões #########
################################################

def get_biddings(ean_artigo):
    conn = db_connection()
    cur = conn.cursor()

    biddings = """
                    SELECT valor, data, utilizador_user_name
                    FROM licitacao
                    WHERE leilao_ean_artigo = %s and validacao = TRUE
                    """

    try:
        cur.execute(biddings, ean_artigo)
        rows = cur.fetchall()
        if len(rows) == 0:
            result = "No biddings to show."
            logger.info(result)
        else:
            result = []
            logger.info("----  List Messages  ----")
            for row in rows:
                logger.debug(row)
                content = {'Valor': row[0], 'Data': row[1], "Username": row[3]}
                result.append(content)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not list all messages.'
    finally:
        if conn is not None:
            conn.close()
    return result


def get_messages(ean_artigo):
    conn = db_connection()
    cur = conn.cursor()

    messages = """
                    SELECT *
                    FROM mensagem
                    WHERE leilao_ean_artigo = %s
                    """

    try:
        cur.execute(messages, ean_artigo)
        rows = cur.fetchall()
        if len(rows) == 0:
            result = "No messages to show."
            logger.info(result)
        else:
            result = []
            logger.info("----  List Messages  ----")
            for row in rows:
                logger.debug(row)
                content = {'Mensagem': row[0],
                           'Data': row[1], "Username": row[3]}
                result.append(content)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not list all messages.'
    finally:
        if conn is not None:
            conn.close()
    return result


def list_details(ean_artigo):
    conn = db_connection()
    cur = conn.cursor()

    descricao_data = """
                            SELECT data_final, descricao
                            FROM leilao, descricao
                            WHERE leilao.ean_artigo = %s and leilao.ean_artigo = descricao.leilao_ean_artigo and leilao.estado = 1
                            """
    value = [ean_artigo]

    result = {}
    try:
        cur.execute(descricao_data, value)
        rows = cur.fetchone()
        if rows is None:
            result = 'Auction not found.'
            logger.error(result)
        else:
            logger.info(rows)
            result["Descricao"] = rows[1]
            result["Data de término"] = rows[0]
            result["Menssagens"] = get_messages(ean_artigo)
            result["Licitacoes"] = get_biddings(ean_artigo)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not list auction details.'
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route('/dbproj/leilao/<leilaoId>/', methods = ['GET'])
def get_auction_details(leilaoId):
    logger.info("### GET - Auction Details (by ID) ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- Auction Details ----")
    logger.debug(f'payload: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if len(row) is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                result = list_details(payload)
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Auctions were not listed.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


##################################################################
########### Listar detalhes dos leilões por Utilizador ###########
##################################################################

def list_biddings_byUser(user_name):
    conn = db_connection()
    cur = conn.cursor()

    list_biddingsbyUser = """
                         SELECT leilao_ean_artigo
                         FROM licitacao
                         WHERE utilizador_user_name like %s
                         """
    value = ([user_name])

    result = {}
    try:
        cur.execute(list_biddingsbyUser, value)
        rows = cur.fetchall()
        if len(rows) == 0:
            result = 'User does not have any biddings.'
            logger.error(result)
        else:
            logger.info(rows)
            auctions_bidded = []
            for row in rows:
                auctions_bidded.append(list_details(row))
            result = auctions_bidded
            return result
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not list auction details.'
    finally:
        if conn is not None:
            conn.close()
    return result

def list_auctions_byUser(user_name):
    conn = db_connection()
    cur = conn.cursor()

    list_auctionsbyUser = """
                          SELECT ean_artigo
                          FROM leilao
                          WHERE utilizador_user_name like %s
                          """
    value = ([user_name])

    result = {}
    try:
        cur.execute(list_auctionsbyUser, value)
        rows = cur.fetchall()
        if len(rows) == 0:
            result = 'User does not have any auctions.'
            logger.error(result)
        else:
            logger.info(rows)
            auctions_created = []
            auctions_bidded = []
            for row in rows:
                auctions_created.append(list_details(row))
            result["Auctions the user made biddings at."] = list_biddings_byUser(user_name)
            result["Auctions the user created."] = auctions_created
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not list auction details.'
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route('/dbproj/user/<userToken>/', methods=['GET'])
def get_auction_details_user(userToken):
    logger.info("### GET - Auction Details (by userID) ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- Auction Details ----")
    logger.debug(f'payload: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if len(row) is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                result = list_auctions_byUser(row[2])
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Auctions were not listed.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


# @app.route('/dbproj/licitar/<leilaoId>/<licitacao>')
##########################################################
# DATABASE ACCESS
##########################################################


def db_connection():
    db = psycopg2.connect(user = "postgres",
                          password = "postgres",
                          host = "localhost",
                          port = "5432",
                          database = "BD_Projeto")
    return db


##########################################################
# MAIN
##########################################################

if __name__ == "__main__":
    # variables
    add_token.counter = 1_000_000_010

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