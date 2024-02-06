import json
import pymysql

# Configuración de la base de datos
rds_endpoint = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

def lambda_handler(event, context):
    # Conectarse a la base de datos
    conn = pymysql.connect(host=rds_endpoint, user=db_username, passwd=db_password, db=db_name)
    
    # Obtener el ID del usuario desde el evento
    user_id = event['queryStringParameters']['userId']

    try:
        # Obtener información del usuario
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE ID = %s", (user_id,))
            user_info = cursor.fetchone()
        
        # Obtener tweets del usuario
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT mensaje FROM mensajes WHERE idUsuario = %s", (user_id,))
            tweets = cursor.fetchall()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Asegúrese de configurar el control de CORS adecuado
            },
            'body': json.dumps({'user_info': user_info, 'tweets': tweets})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        conn.close()
