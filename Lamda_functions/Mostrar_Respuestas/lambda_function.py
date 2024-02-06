import json
import pymysql

# Configuración de la conexión a la base de datos
db_host = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

def lambda_handler(event, context):

    body = json.loads(event.get("body", "{}"))
    
    parent_id = None if "parent_id" not in body else int(body.get('parent_id'))
    
    if not parent_id:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': "Missing parent_id"
        }

    conn = pymysql.connect(db_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()
    
    if not cursor.execute('SELECT * from mensajes where padre = %s ORDER BY fecha_hora DESC',(parent_id,)):
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': "No replies found"
        }

    replies = [
        {
            'idMensaje': x[0],
            'idUsuario': x[1],
            'mensaje': x[2],
            'datoAdjunto': x[3],
            'tipoDato': x[4],
            'padre': x[6],
            'likes': x[7],
            'dislikes': x[8]
        } for x in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    if replies:
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(replies)
        }

    return {
        'statusCode': 400,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': 'No replies found'
    }