import json
import pymysql
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database configuration
rds_endpoint = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

# Main Lambda handler
def lambda_handler(event, context):
    # Connect to the database
    try:
        conn = pymysql.connect(
            host=rds_endpoint,
            user=db_username,
            passwd=db_password,
            db=db_name,
            connect_timeout=5
        )
        logger.info("Successfully connected to the database.")
    except pymysql.MySQLError as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({"error": "Error connecting to the database"})
        }


    # Parse the request body
    try:
        body = json.loads(event.get('body', '{}'))

        id_usuario = body.get('idUsuario')
        mensaje = body.get('mensaje')
        fecha_hora_iso = body.get('fechaHora')
        dato_adjunto = body.get('datoAdjunto', 'None')
        tipo_dato = body.get('tipoDato', 'None')
        id_mensaje_padre = body.get('idMensajePadre')

        if fecha_hora_iso:
            # Replace 'Z' with '+00:00' if it exists
            fecha_hora_iso = fecha_hora_iso.replace('Z', '+00:00')
            fecha_hora_utc = datetime.fromisoformat(fecha_hora_iso)
            fecha_hora_cet = fecha_hora_utc + timedelta(hours=1)  # Adjust for CET timezone
            fecha_hora_mysql = fecha_hora_cet.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # Handle the case where fecha_hora_iso is None
            fecha_hora_mysql = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        with conn.cursor() as cursor:
            # Update the response count for the parent tweet
            if id_mensaje_padre:
                update_sql = """
                UPDATE mensajes
                SET padre = IFNULL(padre, 0) + 1
                WHERE idMensaje = %s
                """
                cursor.execute(update_sql, (id_mensaje_padre,))

            # Insert the new message
            insert_sql = """
            INSERT INTO mensajes (idUsuario, mensaje, fecha_hora, datoAdjunto, tipoDato, padre)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (id_usuario, mensaje, fecha_hora_mysql, dato_adjunto, tipo_dato, id_mensaje_padre))
            conn.commit()
        logger.info("Message successfully inserted.")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps("Message successfully inserted.")
        }
    except Exception as e:
        logger.error(f"Error processing the request: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({"error": "Error inserting the message"})
        }
    finally:
        if conn:
            conn.close()
