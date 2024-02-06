import json
import pymysql
import logging
from datetime import datetime, timedelta

# Configuración del logger para depuración
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Puedes cambiar a DEBUG para más detalle

# Configuración de la base de datos RDS
rds_endpoint = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

def lambda_handler(event, context):
    # Intenta establecer la conexión a la base de datos
    try:
        conn = pymysql.connect(
            host=rds_endpoint,
            user=db_username,
            passwd=db_password,
            db=db_name,
            connect_timeout=5
        )
        logger.info("Conexión a base de datos establecida")
    except pymysql.MySQLError as e:
        logger.error(f"Error al conectar a MySQL: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps("Error al conectar a la base de datos")
        }

    # Parsea el cuerpo de la solicitud
    try:
        body = json.loads(event['body'])
        id_usuario = body['idUsuario']
        mensaje = body['mensaje']
        fecha_hora_iso = body['fechaHora']  # Fecha y hora en formato ISO
        dato_adjunto = body.get('datoAdjunto')
        tipo_dato = body.get('tipoDato')
        padre_id = int(body.get('padre'))

        # Convertir la fecha y hora ISO a formato compatible con MySQL
        fecha_hora_utc = datetime.fromisoformat(fecha_hora_iso.replace('Z', '+00:00'))
        # Ajustar para la zona horaria de España (CET/CEST)
        # Asumiendo +1 hora para CET. Deberías ajustar esto según sea necesario, por ejemplo, usando +2 horas para CEST
        fecha_hora_cet = fecha_hora_utc + timedelta(hours=1)
        fecha_hora_mysql = fecha_hora_cet.strftime('%Y-%m-%d %H:%M:%S')

        with conn.cursor() as cursor:
            sql = """
            INSERT INTO mensajes (idUsuario, mensaje, fecha_hora, datoAdjunto, tipoDato, padre)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (id_usuario, mensaje, fecha_hora_mysql, dato_adjunto, tipo_dato, padre_id if padre_id != -1 else None))
            conn.commit()
        logger.info("Mensaje insertado correctamente")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps("Mensaje insertado con éxito")
        }
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps("Error al insertar el mensaje")
        }
    finally:
        conn.close()  # Asegúrate de cerrar la conexión a la base de datos
