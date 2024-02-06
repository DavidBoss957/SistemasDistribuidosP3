import json
import pymysql
import base64
from datetime import datetime

# Configuración de la conexión a la base de datos
db_host = "44.205.178.122"
db_username = "twitter"
db_password = "twitter"
db_name = "twitter"

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

def lambda_handler(event, context):

    body = json.loads(event.get("body", "{}"))

    if "userId" not in body or "file" not in body :
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': "No userId or file"
        }
        
    conn = pymysql.connect(db_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()

    user_id = body.get("userId", None)
    
    if user_id:
        cursor.execute("INSERT INTO mensajes (user_id, message, adjunct) VALUES (%s, %s, %s)",
                       (user_id, body.get('message'), body.get('adjunct')))
        conn.commit()

    cursor.close()
    conn.close()

    if not user_id:
        return {
            'statusCode': 401,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': 'Message not created'
        }

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': 'Message created'
    }