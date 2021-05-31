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
# Sofia Alves - 2019227240
# University of Coimbra


from email import message
from pickle import TRUE
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
    Aplicação de Leilões Online  <br/>
    <br/>
    BD 2021 Projeto<br/>
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


@app.route("/dbproj/user/", methods=['POST'])
def add_users():
    logger.info("### POST - Add new user ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'user_name' not in payload.keys() or 'email' not in payload.keys() or 'password' not in payload.keys():
        result = 'The informations required no regist a new user are incomplete.'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

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


@app.route("/dbproj/admin/", methods=['POST'])
def add_admin():
    logger.info("### POST - Add new admin ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'user_name' not in payload.keys() or 'email' not in payload.keys() or 'password' not in payload.keys():
        result = 'The informations required no regist a new admin are incomplete.'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

    logger.info("---- New Admin ----")
    logger.debug(f'payload: {payload}')

    statement = """
                INSERT INTO utilizador (user_name, email, password, estado, avaliacao, admin)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

    values = (payload["user_name"], payload["email"],
              payload["password"], True, "0", True)

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
        result = 'Username and password are required to autenticate!'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

    logger.info("---- Autenticate User/Admin ----")
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


def add_description(titulo, descricao, ean_artigo):
    conn = db_connection()
    cur = conn.cursor()

    statement = """
                INSERT INTO descricao (titulo, descricao, data, leilao_ean_artigo)
                VALUES (%s,%s, %s, %s)
                """

    values = (titulo, descricao, datetime.now(), int(ean_artigo))

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


def create_auction(payload, user_name):
    logger.info("entrou em create_auction")
    conn = db_connection()
    cur = conn.cursor()

    logger.info(payload)

    statement = """
                INSERT INTO leilao (vencedor, ean_artigo, estado, data_final, data_inicial, preco_min, utilizador_user_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

    values = (None, payload["ean_artigo"], "1",
              payload["data_final"], datetime.now(), payload["preco_min"], user_name)

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        add_description(payload["titulo"],
                        payload["descricao"], payload["ean_artigo"])
        result = 'Auction created with success!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Auction was not created.'
    finally:
        if conn is not None:
            conn.close()
    logger.info(result)
    return result


@app.route("/dbproj/leilao/", methods=['POST'])
def new_auction():
    logger.info("### POST - Add new auction ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'valor_token' not in payload.keys() or 'titulo' not in payload.keys() or 'ean_artigo' not in payload.keys() or 'data_final' not in payload.keys() or 'preco_min' not in payload.keys() or 'descricao' not in payload.keys():
        result = 'The informations required no create a new auction are incomplete.'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

    logger.info("---- New auction ----")
    logger.debug(f'payload: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        logger.info(f'fow: {row}')
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            user_info = get_user(row[2])
            if (user_info[3] == False):
                result = "The token given is from a banned user."
                logger.error(result)
            else:
                if row[1] > datetime.now():
                    logger.info(f"row: {row}")
                    result = create_auction(payload, row[2])
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

def list_all_auctions():
    conn = db_connection()
    cur = conn.cursor()

    list_auctions = """
                    SELECT leilao_ean_artigo, titulo, data, descricao
                    FROM descricao d, leilao
                    GROUP BY leilao_ean_artigo, titulo, data, descricao, leilao.estado
                    HAVING data = (SELECT MAX(data) FROM descricao WHERE leilao_ean_artigo = d.leilao_ean_artigo) and  leilao.estado = 1
                    ORDER BY  data,leilao_ean_artigo 
                    """

    try:
        cur.execute(list_auctions)
        rows = cur.fetchall()
        logger.info(rows)
        result = []
        logger.info("----  List Auctions  ----")
        for row in rows:
            logger.debug(row)
            content = {'LeilaoId': row[0],
                       'Titulo': row[1], 'Descricao': row[3]}
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

    if 'valor_token' not in payload.keys():
        result = 'Token required to make this operations!'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

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

def list_by_ean(keyword):
    conn = db_connection()
    cur = conn.cursor()

    list_auctions = """
                    SELECT descricao.titulo, descricao
                    FROM leilao, descricao
                    WHERE leilao.ean_artigo = %s and leilao.ean_artigo = descricao.leilao_ean_artigo and estado = 1
                    """
    value = [keyword]

    try:
        cur.execute(list_auctions, value)
        row = cur.fetchone()
        if row is None:
            result = 'No auctions found with the ean specified'
            logger.error(result)
        else:
            logger.info(row)
            logger.info("----  List Auctions by ean ----")
            logger.debug(row)
            result = {'Título': row[0], 'Descrição': row[1]}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not list all auctions.'
    finally:
        if conn is not None:
            conn.close()
    return result


def list_by_description(keyword):
    conn = db_connection()
    cur = conn.cursor()

    list_auctions = """
                        SELECT distinct descricao.titulo, descricao
                        FROM leilao, descricao
                        WHERE estado = 1 and descricao = %s
                        """
    value = [keyword]

    try:
        cur.execute(list_auctions, value)
        rows = cur.fetchall()
        if len(rows) == 0:
            result = 'No autions with the specified description.'
            logger.error(result)
        else:
            result = []
            logger.info(rows)
            logger.info("----  List Auctions by ean ----")
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


def list_searched_auctions(keyword):
    result = list_by_ean(keyword)
    if result == 'No auctions found with the specified ean' or result == 'Could not list all auctions.':
        result = list_by_description(keyword)
        if result == 'No autions with the specified description.' or result == 'Could not list all auctions.':
            result = 'Invalid keyword or no auctions found'

    return result


@ app.route('/dbproj/leiloes/<keyword>/', methods=['GET'])
def search_auction(keyword):
    logger.info("### GET - List Auctions (by ID or description) ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'valor_token' not in payload.keys():
        result = 'Token required to make this operations!'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

    logger.info("---- Search Auctions ----")
    logger.debug(f'Token Id: {payload}\nOption: {keyword}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                result = list_searched_auctions(keyword)
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
                    WHERE leilao_ean_artigo = %s and validacao = True
                    """

    try:
        cur.execute(biddings, [ean_artigo])
        rows = cur.fetchall()
        if len(rows) == 0:
            result = "No biddings to show."
            logger.info(result)
        else:
            result = []
            logger.info("----  List Biddings  ----")
            logger.info(f'Rows: {rows}')
            for row in rows:
                logger.debug(row)
                content = {'Valor': row[0], 'Data': row[1], "Username": row[2]}
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
        cur.execute(messages, [ean_artigo])
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
            result["Mensagens"] = get_messages(ean_artigo)
            result["Licitacoes"] = get_biddings(ean_artigo)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = '1) Could not list auction details.'
    finally:
        if conn is not None:
            conn.close()
    logger.info(f"result do list_details: {result}")
    return result


@app.route('/dbproj/leilao/<leilaoId>/', methods=['GET'])
def get_auction_details(leilaoId):
    logger.info("### GET - Auction Details (by ID) ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'valor_token' not in payload.keys():
        result = 'Token required to make this operations!'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

    logger.info("---- Auction Details ----")
    logger.debug(f'Token Id: {payload}\nLeilao Id: {leilaoId}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if len(row) is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                result = list_details(leilaoId)
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
                        SELECT distinct leilao_ean_artigo
                        FROM licitacao
                        WHERE utilizador_user_name like %s
                        """
    value = ([user_name])

    try:
        # retorna o ean de todos os leiloes onde o user licitou
        cur.execute(list_biddingsbyUser, value)
        rows = cur.fetchall()
        logger.info(f'leiloes licitados: {rows}')
        if len(rows) == 0:
            result = 'User does not have any biddings.'
            logger.error(result)
        else:
            logger.info(rows)
            auctions_bidded = []
            for row in rows:
                logger.info(row)
                auctions_bidded.append(list_details(row))
            logger.info(auctions_bidded)
            return auctions_bidded
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = '2) Could not list auction details.'
    finally:
        if conn is not None:
            conn.close()
    logger.info(f"result de list_biddingsByUser: {result}")
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
        rows = cur.fetchall()  # retorna o ean de todos os leiloes criados pelo user
        if len(rows) == 0:
            result1 = 'User does not have any auctions.'
            logger.error(result)
        else:
            logger.info(rows)
            auctions_created = []
            for row in rows:
                auctions_created.append(list_details(row))
            result1 = auctions_created
        auctions_created_by_user = {"Auctions created by the user": result1}
        result.update(auctions_created_by_user)
        auctions_bidded = list_biddings_byUser(user_name)
        biddings = {"Auctions the user made biddings at": auctions_bidded}
        result.update(biddings)

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = '3) Could not list auction details.'
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route('/dbproj/user/<userToken>/', methods=['GET'])
def get_auction_details_user(userToken):
    logger.info("### GET - Auction Details (by userID) ###")

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- Auction Details ----")
    logger.debug(f'user token: {userToken}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [userToken])
        row = cur.fetchone()
        if len(row) is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                result = list_auctions_byUser(row[2])
            else:
                result = "Session expired."
                delete_token(userToken)
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Auctions were not listed.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


########################################
########### Fazer licitações ###########
########################################

def add_biding(ean_artigo, licitacao, user_name):
    conn = db_connection()
    cur = conn.cursor()

    add_bidding = """
                INSERT INTO licitacao (valor, data, validacao, utilizador_user_name, leilao_ean_artigo)
                VALUES (%s, %s, %s, %s, %s)
                """
    values = (licitacao, datetime.now(),
              "True", user_name, ean_artigo)

    notify_all(ean_artigo, 0)

    try:
        cur.execute(add_bidding, values)
        cur.execute("commit")
        result = 'The bidding was added.'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Bidding operations could not be done.'
    finally:
        if conn is not None:
            conn.close()
    return result


def confirm_bidding(ean_artigo, licitacao, user_name):
    logger.info('entrou em confirm_bidding')
    conn = db_connection()
    cur = conn.cursor()

    bid = """
            SELECT max(valor)
            FROM licitacao
            WHERE leilao_ean_artigo = %s and validacao = True
            """
    value_in = ([ean_artigo])
    try:
        cur.execute(bid, value_in)
        row = cur.fetchone()
        if row[0] is not None and row[0] < licitacao:
            add_biding(ean_artigo, licitacao, user_name)
            result = 'Bidding was added.'
        elif row[0] is None:
            add_biding(ean_artigo, licitacao, user_name)
            result = 'Bidding was added.'
        else:
            result = 'Invalid bidding.'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Bidding operations could not be done.'
    finally:
        if conn is not None:
            conn.close()
    return result


def bidding(user_name, leilaoId, licitacao):
    conn = db_connection()
    cur = conn.cursor()

    licitacao = float(licitacao)
    leilaoId = int(leilaoId)

    make_bidding = """
                SELECT *
                FROM leilao
                WHERE ean_artigo = %s and estado = 1 and preco_min < %s
                """
    values = (leilaoId, licitacao)

    try:
        cur.execute(make_bidding, values)

        row = cur.fetchone()
        logger.info(f'Row: {row}')
        if row is None:
            result = 'It is not possible to bid this article.'
            logger.error(result)
        elif row[6] == user_name:
            result = 'Auction creator doesn\'t have the permission to bid in his own auction'
            logger.info(result)
        else:
            result = confirm_bidding(row[1], licitacao, user_name)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Bidding operations could not be done.'
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route('/dbproj/licitar/<leilaoId>/<licitacao>/', methods=['GET'])
def make_bidding(leilaoId, licitacao):
    logger.info("### GET - Make bidding ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'valor_token' not in payload.keys():
        result = 'Token required to make this operations!'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

    logger.info("---- Bidding ----")
    logger.debug(f'Token value: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            user_info = get_user(row[2])
            if (user_info[3] == False):
                result = "The token given is from a banned user"
                logger.error(result)
            else:
                if row[1] > datetime.now():
                    result = bidding(row[2], leilaoId, licitacao)
                else:
                    result = "Session expired."
                    delete_token(payload["valor_token"])
                    logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Bidding operation could not be done.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


########################################
########### Editar Leilao ##############
########################################

def get_description(ean_artigo):
    conn = db_connection()
    cur = conn.cursor()

    last_description = """
                        SELECT titulo, descricao, leilao_ean_artigo
                        FROM (SELECT *
                                FROM descricao
                                ORDER BY data DESC) as tudo, leilao
                        WHERE leilao_ean_artigo = %s and leilao.estado = 1
                        LIMIT 1
                        """

    values = ([ean_artigo])
    try:
        cur.execute(last_description, values)
        row = cur.fetchone()
        logger.info(f'Row: {row}')
        if row is None:
            result = 'No descriptions inserted.'
            logger.error(result)
        else:
            result = row
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not find description.'
    finally:
        if conn is not None:
            conn.close()
    return result


def edit_auction_properties(payload, ean_artigo, user_editing):
    conn = db_connection()
    cur = conn.cursor()

    last_auction = get_description(ean_artigo)
    logger.info(f'last_auction: {last_auction}')

    auction_info = get_auction(ean_artigo)
    if user_editing != auction_info[6]:
        result = "Only the creator of this auction has the permission to edit its details."

    else:
        if last_auction != 'No descriptions inserted' or last_auction != 'Could not find description':

            edit_auction = """
                            INSERT INTO descricao(titulo, descricao, data, leilao_ean_artigo)
                            VALUES (%s,%s,%s,%s)
                            """

            if "titulo" in payload.keys() and "descricao" not in payload.keys():
                values = (payload["titulo"], last_auction[1],
                          datetime.now(), ean_artigo)

            elif "descricao" in payload.keys() and "titulo" not in payload.keys():
                values = (last_auction[0], payload["descricao"],
                          datetime.now(), ean_artigo)

            elif "titulo" in payload.keys() and "descricao" in payload.keys():
                values = (payload["titulo"], payload["descricao"],
                          datetime.now(), ean_artigo)

            else:
                result = 'Title or description are required to edit an auction.'
                logger.error(result)
                if conn is not None:
                    conn.close()
                return result

            try:
                cur.execute(edit_auction, values)
                cur.execute("commit")
                result = 'New description added.'
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)
                result = 'Could not add description.'

    if conn is not None:
        conn.close()
    return result


@app.route('/dbproj/leilao/<idLeilao>/', methods=['PUT'])
def edit_auction(idLeilao):
    logger.info("### PUT - Auction Details ) ###")
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
                result = edit_auction_properties(payload, idLeilao, row[2])
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Bidding operation could not be done.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


###############################################################
##################### Mensagens do Mural ######################
###############################################################

def verify_auction_state(leilaoId):
    conn = db_connection()
    cur = conn.cursor()

    verify_ean = """
                    SELECT estado, ean_artigo
                    FROM leilao
                    WHERE ean_artigo = %s
                """
    values = ([leilaoId])

    try:
        cur.execute(verify_ean, values)
        row = cur.fetchone()
        if row is None:
            result = "Invalid ean"
        else:
            result = row
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "Could not verify auction."
    finally:
        if conn is not None:
            conn.close()
    return result


def create_message(leilaoId, message, username):
    conn = db_connection()
    cur = conn.cursor()

    add_bidding = """
                    INSERT INTO mensagem (descricao, data, leilao_ean_artigo, utilizador_user_name)
                    VALUES (%s, %s, %s, %s)
                """
    values = (message, datetime.now(),
              leilaoId, username)

    try:
        cur.execute(add_bidding, values)
        result = verify_auction_state(leilaoId)
        logger.info(result)
        if result != "Invalid ean":
            if result[1] == 0:
                result = "Auction has already finnished."
            else:
                cur.execute("commit")
                notify_all(leilaoId, 1)  # Estado 1 = notif. messagens no mural
                result = "Message was written."
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "Could not write the message."
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route("/dbproj/mural/<leilaoId>/<message>/", methods=['POST'])
def write_message(leilaoId, message):
    logger.info("### POST - Writing new message in auction's mural ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'valor_token' not in payload.keys():
        result = 'Token required to make this operations!'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

    logger.info("---- New message ----")
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
                logger.info(f"row: {row}")
                result = create_message(leilaoId, message, row[2])
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


########################################
######## Notificar utilizadores ########
########################################

"""
 Notifica utilizadores que escreveram no mural
"""


def get_bidders(ean_artigo, message):
    logger.info('entrou em get_bidders')
    conn = db_connection()
    cur = conn.cursor()

    users_notified = ""
    if message == "Canceled auction":
        users_notified = """
                        SELECT distinct utilizador_user_name
                        FROM licitacao
                        WHERE leilao_ean_artigo = %s
                    """
    elif message == "New message in mural":
        users_notified = """
                        SELECT distinct utilizador_user_name
                        FROM mensagem
                        WHERE leilao_ean_artigo = %s
                    """
    elif message == "Bidding exceeded":
        users_notified = """
                        SELECT  utilizador_user_name
                        FROM (SELECT *
                                FROM licitacao
                                ORDER BY valor DESC) as tudo
                        WHERE leilao_ean_artigo = %s
                        LIMIT 1
                    """
    value = ([ean_artigo])

    try:
        cur.execute(users_notified, value)
        users = cur.fetchall()
        logger.info(f"users affected: {users}")
        if len(users) == 0:
            result = "No messages"
        else:
            result = users
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "Could not verify message table."
    finally:
        if conn is not None:
            conn.close()
    logger.info(f'Get_bidders return value: {result}')
    return result


def notify_bidder(ean_artigo, user_name, notify, message):
    conn = db_connection()
    cur = conn.cursor()

    values = (message, ean_artigo, user_name, datetime.now())
    try:
        cur.execute(notify, values)
        cur.execute("commit")
        result = 'User was notified.'
        logger.info(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'User was not notified.'
    finally:
        if conn is not None:
            conn.close()
    return result


def notify_all_bidders(ean_artigo, message):
    users_notified = 0
    # retorna todos os users que enviaram mensagens no leilao
    result = get_bidders(ean_artigo, message)
    if result != "No messages" and result != "Could not verify message table.":
        notify = """
                    INSERT INTO notificacao(descricao, leilao_ean_artigo, utilizador_user_name, data_entrega)
                    VALUES (%s,%s,%s,%s)
                    """
        for user in result:
            logger.info(f'user to notify: {user}')
            result1 = notify_bidder(ean_artigo, user, notify, message)
            if result1 == 'User was notified.':
                users_notified += 1
        if users_notified != len(result):
            result = "Not all users were notified"
            logger.error(result)
    else:
        logger.error(result)


"""
 Notifica utilizador que a sua licitação foi superada
"""

"""
 Notifica utilizador que criou o leilão
"""


def get_auction(ean_artigo):
    conn = db_connection()
    cur = conn.cursor()

    auction = """
              SELECT *
              FROM leilao
              WHERE ean_artigo = %s
              """
    values = ([ean_artigo])
    try:
        cur.execute(auction, values)
        row = cur.fetchone()
        if row is None:
            result = 'No auction found.'
            logger.error(result)
        else:
            result = row
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not verify auction.'
    finally:
        if conn is not None:
            conn.close()
    return result


def notify_creator(ean_artigo, notify, result, message):
    conn = db_connection()
    cur = conn.cursor()

    values = (message, ean_artigo, result[5], datetime.now())

    try:
        cur.execute(notify, values)
        cur.execute("commit")
        result = 'User was notified.'
        logger.info(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'User was not notified.'
    finally:
        if conn is not None:
            conn.close()
    return result


def notify_auction_creator(ean_artigo, message):
    result = get_auction(ean_artigo)
    if result != 'No auction found.' and result != 'Could not verify auction.':
        notify = """
                    INSERT INTO notificacao(descricao, leilao_ean_artigo, utilizador_user_name,data_entrega)
                    VALUES (%s,%s,%s,%s)
                    """
        result = notify_creator(ean_artigo, notify, result, message)
    logger.error(result)


def notify_all(ean_artigo, state):
    message = ""
    if state == 2:
        message = "Canceled auction"
        notify_all_bidders(ean_artigo, message)
        notify_auction_creator(ean_artigo, message)
    elif state == 1:
        message = "New message in mural"
        notify_all_bidders(ean_artigo, message)
        notify_auction_creator(ean_artigo, message)
    elif state == 0:
        message = "Bidding exceeded"
        notify_all_bidders(ean_artigo, message)


"""
 FUNCIONALIDADE que permite verificar a caixa de entrada do utilizador que iniciou uma sessão.
"""


def check_mail_box(user_name):
    conn = db_connection()
    cur = conn.cursor()

    logger.info('entrou no check_mail_box')

    notifications = """
                    SELECT * 
                    FROM notificacao
                    WHERE utilizador_user_name = %s
                    """

    try:
        cur.execute(notifications, [user_name])
        rows = cur.fetchall()
        if len(rows) == 0:
            result = 'No notifications yet.'
            logger.info(result)
        else:
            result = rows
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not verify notificacao table'
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route("/dbproj/caixa_entrada/", methods=['GET'])
def get_notifications():
    logger.info("### GET - Checking notifications ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'valor_token' not in payload.keys():
        result = 'Token required to make this operations!'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

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
                logger.info(f"row: {row}")
                result = check_mail_box(row[2])
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


################################
####### Terminar leilão ########
################################

def update_auction(maiorLicitacao):
    conn = db_connection()
    cur = conn.cursor()

    update_auction = """
                    UPDATE leilao 
                    SET estado = 0, vencedor = %s 
                    WHERE ean_artigo = %s and data_final < %s
                    """
    values = (maiorLicitacao[3], maiorLicitacao[4], datetime.now())

    try:
        cur.execute(update_auction, values)
        cur.execute("commit")
        result = f"The auction finished. The winner was {maiorLicitacao[3]} and its bidding was {maiorLicitacao[0]}"
        logger.info(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "The auction could not be finished."
    finally:
        if conn is not None:
            conn.close()
    return result


def confirm_finish_auction(leilaoId):
    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT * FROM licitacao WHERE leilao_ean_artigo = %s ORDER BY valor DESC LIMIT 1", [leilaoId])
        row = cur.fetchone()
        logger.info(f"Row: {row}")
        if row == None:
            result = "The auction did not have any biddings. There is no winner."
        else:
            cur.execute("commit")
            result = update_auction(row)
            logger.info(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "The biddings could not be found."
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route("/dbproj/leilao/terminar/<leilaoId>/", methods=['PUT'])
def terminate_auction(leilaoId):
    logger.info("### PUT - Ending Auction ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- Ending Auction ----")
    logger.debug(f'Token value: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                logger.info(f"Row: {row}")
                result = confirm_finish_auction(leilaoId)
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Token value could not be found.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


##########################################################
# FUNÇÕES DO ADMINISTRADOR ###############################
##########################################################


################################
####### Cancelar leilão ########
################################

def verify_admin(user_name):
    user_info = get_user(user_name)
    return user_info[5] == True


def get_user(user_name):
    conn = db_connection()
    cur = conn.cursor()

    auction = """
              SELECT *
              FROM utilizador
              WHERE user_name = %s
              """
    values = ([user_name])
    try:
        cur.execute(auction, values)
        row = cur.fetchone()
        if row is None:
            result = 'No user found.'
            logger.error(result)
        else:
            result = row
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Could not verify utilizador table.'
    finally:
        if conn is not None:
            conn.close()
    return result


def confirm_cancel_auction(leilaoId, user_name):
    conn = db_connection()
    cur = conn.cursor()

    auction_info = get_auction(leilaoId)

    if verify_admin(user_name) == False:
        result = 'Only admin has this permission'

    elif auction_info[2] == 2:
        result = 'Auction was already canceled'

    else:
        try:
            notify_all(leilaoId, 2)
            cur.execute(
                "UPDATE leilao SET estado = 2 WHERE ean_artigo = %s", [leilaoId])
            cur.execute("commit")
            result = "The auction was canceled."
            logger.info(result)

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = "The auction could not be canceled."

    if conn is not None:
        conn.close()
    return result


@app.route("/dbproj/admin/<leilaoId>/", methods=['PUT'])
def cancel_auction(leilaoId):
    logger.info("### PUT - Cancel an auction ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if 'valor_token' not in payload.keys():
        result = 'Token required to make this operations!'
        logger.error(result)
        if conn is not None:
            conn.close()
        return jsonify(result)

    logger.info("---- Cancel Auction ----")
    logger.debug(f'Token value: {payload}')

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                logger.info(f"Row: {row}")
                result = confirm_cancel_auction(leilaoId, row[2])
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Token value could not be found.'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


################################
####### Banir utilizador #######
################################

def invalidate_biddings(user_name):
    conn = db_connection()
    cur = conn.cursor()

    update_auction = """
                    UPDATE licitacao
                    SET validacao = False 
                    WHERE utilizador_user_name = %s
                    """
    value = ([user_name])

    try:
        cur.execute(update_auction, value)
        cur.execute("commit")
        result = "Biddings from user are now invalid."
        logger.info(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "The biddings could not be made invalid."
    finally:
        if conn is not None:
            conn.close()
    return result


def remove_biddings(user_name):
    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT * FROM licitacao WHERE utilizador_user_name = %s", [user_name])
        rows = cur.fetchall()
        if len(rows) == 0:
            result = "User doesn't have bidders."
            logger.error(result)
        else:
            result = invalidate_biddings(user_name)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "The user's biddings are not invalid."
    finally:
        if conn is not None:
            conn.close()
    return result


def confirm_ban_user(admin, user_name):
    conn = db_connection()
    cur = conn.cursor()

    result = ""
    try:
        cur.execute(
            "SELECT * FROM leilao WHERE utilizador_user_name = %s", [user_name])
        rows = cur.fetchall()
        if len(rows) == 0:
            result = "User did not create any auctions."
            logger.error(result)
        else:
            for row in rows:
                confirm_cancel_auction(row[1], admin)
                create_message(
                    row[1], "This auction was canceled. We are sorry for the inconvinience.", admin)
            result = "The aucions were canceled."
        result += remove_biddings(user_name)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "The user's auctions could not be canceled."
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route("/dbproj/admin/banir/<user>", methods=['PUT'])
def ban_utilizador(user_name):
    logger.info("### PUT - Ban user ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- Banning User ----")
    logger.debug(f"Token value: {payload}")

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                confirm_ban_user(row[2], user_name)
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "Token could not be found."
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


################################
##### Obter estatísticas #######
################################

def present_statisticsTOP10Wins():
    conn = db_connection()
    cur = conn.cursor()

    top10_wins = """
                SELECT vencedor, COUNT(ean_artigo)
                FROM leilao
                GROUP BY vencedor, leilao.estado
                HAVING leilao.estado = 0
                ORDER BY COUNT(ean_artigo) DESC
                LIMIT 10
                """

    try:
        cur.execute(top10_wins)
        rows = cur.fetchall()
        if len(rows) == 0:
            result = "TOP 10 of winners could not be found."
            logger.error(result)
        else:
            logger.info(rows)
            top10 = []
            logger.info("----  List TP10 Winners  ----")
            for row in rows:
                logger.debug(row)
                content = {"User": row[0], "Auctions": row[1]}
                top10.append(content)
            result = top10
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "The auction could not be canceled."
    finally:
        if conn is not None:
            conn.close()
    return result


def present_statisticsAuctions():
    conn = db_connection()
    cur = conn.cursor()

    total_auctions = """
                    SELECT count(ean_artigo)
                    FROM leilao
                    WHERE data_inicial = data_inicial - 10
                    """

    try:
        cur.execute(total_auctions)
        row = cur.fetchall()
        if row == None:
            result = "0 auctions in the last 10 days."
            logger.error(result)
        else:
            logger.info(row)
            logger.info("---- Number of auctions in the last 10 days ----")
            result = row
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "The auction could not be canceled."
    finally:
        if conn is not None:
            conn.close()
    return result


def present_statisticsTOP10Auctions():
    conn = db_connection()
    cur = conn.cursor()

    top10_auctions = """
                    SELECT utilizador_user_name, count(ean_artigo)
                    FROM leilao
                    GROUP BY utilizador_user_name
                    ORDER BY count(ean_artigo) DESC
                    LIMIT 10
                    """

    result = {}
    try:
        cur.execute(top10_auctions)
        rows = cur.fetchall()
        logger.info(f"top10_auctions: {rows}")
        if len(rows) == 0:
            result = "TOP 10 could not be found."
            logger.error(result)
        else:
            logger.info(rows)
            top10 = []
            logger.info("----  List TP10 Auctions  ----")
            for row in rows:
                logger.debug(row)
                content = {"User": row[0], "Auctions": row[1]}
                top10.append(content)
            result["TOP10 - More Auctions"] = top10
            result["TOP10 - More Wins"] = present_statisticsTOP10Wins()
            result["Number of Auctions (last 10 days)"] = present_statisticsAuctions(
            )
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "The auction could not be canceled."
    finally:
        if conn is not None:
            conn.close()
    return result


@app.route("/dbproj/admin/estatisticas/", methods=['GET'])
def show_statistics():
    logger.info("### GET - Show auction's statistics ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- Show Statistics ----")
    logger.debug(f"Token value: {payload}")

    try:
        cur.execute("SELECT * FROM token WHERE valor = %s",
                    [payload["valor_token"]])
        row = cur.fetchone()
        if row is None:
            result = 'User is not logged in.'
            logger.error(result)
        else:
            if row[1] > datetime.now():
                logger.info(f"Row: {row}")
                result = present_statisticsTOP10Auctions()
            else:
                result = "Session expired."
                delete_token(payload["valor_token"])
                logger.error(result)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = "Token could not be found."
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
                          port="5432",
                          database="BD_Projeto")
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

    time.sleep(1)  # :-)

    logger.info("\n---------------------------------------------------------------\n" +
                "API v1.0 online: http://localhost:8080/departments/\n\n")

    app.run(host="localhost", port=8080,  debug=True, threaded=True)
