import json
import pymysql
import logging

# Configuración del logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de la base de datos
db_host = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

def lambda_handler(event, context):
    logger.info(f"Received event: {event}")

    # Asegurarse de que la solicitud sea un POST o GET
    http_method = event.get('requestContext', {}).get('http', {}).get('method')
    if http_method not in ['POST', 'GET']:
        logger.warning(f"Method not allowed: {http_method}")
        return {
            'statusCode': 405,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method Not Allowed'})
        }

    # Extraer el userId dependiendo del método
    userId = None
    if http_method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            userId = body.get('userId')
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing request body: {e}")
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invalid request body'})
            }
    else:  # GET method
        userId = event.get('queryStringParameters', {}).get('userId')

    if not userId:
        logger.warning("userId not provided")
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'userId not provided'})
        }

    try:
        # Intentar conectar a la base de datos
        conn = pymysql.connect(db_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=5)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        logger.info("Successfully connected to the database")

        # Obtener información del usuario
        cursor.execute("SELECT nombre_usuario, correo_electronico, biografia FROM usuarios WHERE ID = %s", (userId,))
        user_info = cursor.fetchone()
        logger.info(f"User info fetched: {user_info}")

        # Obtener tweets del usuario
        cursor.execute("SELECT mensaje FROM tweets WHERE idUsuario = %s ORDER BY fecha_hora DESC", (userId,))
        tweets = cursor.fetchall()
        logger.info(f"User tweets fetched: {tweets}")

        # Si no se encuentra el usuario, devuelve un error
        if not user_info:
            logger.warning("User not found")
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'User not found'})
            }

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'user_info': user_info, 'tweets': tweets})
        }
    except Exception as e:
        logger.error(f"Error during database operation: {e}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
    finally:
        if conn:
            cursor.close()
            conn.close()
