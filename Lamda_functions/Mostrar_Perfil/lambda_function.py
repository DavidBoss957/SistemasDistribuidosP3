import json
import pymysql
import traceback

# Configuración de la base de datos
host = '44.205.178.122'
user = 'twitter'
password = 'twitter'
database = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

# Configuración de las cabeceras CORS
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
}

def lambda_handler(event, context):
    print("Evento recibido:", event)

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'CORS preflight successful'})}

    try:
        conn = pymysql.connect(host, user=user, password=password, database=database, connect_timeout=5)
        body = json.loads(event.get('body', '{}'))
        print("Cuerpo de la solicitud:", body)

        action = body.get('action')
        print("Acción:", action)

        if action == 'getUserInfo':
            userId = body.get('userId')
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # Obtener información del usuario
                cursor.execute("SELECT * FROM usuarios WHERE ID = %s", (userId,))
                user_info = cursor.fetchone()

                # Obtener tweets del usuario
                cursor.execute("SELECT mensaje FROM mensajes WHERE idUsuario = %s", (userId,))
                tweets = cursor.fetchall()

                if user_info:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({'user_info': user_info, 'tweets': tweets})
                    }
                else:
                    return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'message': 'User not found'})}

        else:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Action not recognized'})}

    except Exception as e:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        print(f"Error: {e}")
        print(traceback_str)
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e), 'traceback': traceback_str})
        }
    
    finally:
        if conn:
            conn.close()
