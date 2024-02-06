import json
import pymysql
import logging
from datetime import datetime

# Configure logging for debugging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database configuration
rds_endpoint = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

def lambda_handler(event, context):
    try:
        conn = pymysql.connect(
            host=rds_endpoint,
            user=db_username,
            passwd=db_password,
            db=db_name,
            connect_timeout=5,
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Successfully connected to the database.")
    except pymysql.MySQLError as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": "Error connecting to the database"})
        }

    tweet_id = event.get('queryStringParameters', {}).get('idMensaje')

    try:
        with conn.cursor() as cursor:
            if tweet_id:
                query = """
                SELECT mensajes.idMensaje, usuarios.nombre_usuario, mensajes.mensaje, mensajes.fecha_hora, mensajes.datoAdjunto, mensajes.tipoDato, usuarios.ID
                FROM mensajes
                INNER JOIN usuarios ON mensajes.idUsuario = usuarios.ID
                WHERE mensajes.idMensaje = %s 
                """
                cursor.execute(query, (tweet_id,))
            else:
                query = """
                SELECT mensajes.idMensaje, usuarios.nombre_usuario, mensajes.mensaje, mensajes.fecha_hora, mensajes.datoAdjunto, mensajes.tipoDato, usuarios.ID
                FROM mensajes
                INNER JOIN usuarios ON mensajes.idUsuario = usuarios.ID
                WHERE mensajes.padre is NULL
                ORDER BY mensajes.fecha_hora DESC 
                """
                cursor.execute(query)

            result = cursor.fetchall()

        result = json.loads(json.dumps(result, default=datetime_converter))

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": "Error fetching messages"})
        }
    finally:
        if conn:
            conn.close()