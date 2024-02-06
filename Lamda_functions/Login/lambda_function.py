import json
import pymysql

# Configuración de la conexión a la base de datos
db_host = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

def lambda_handler(event, context):
    
    body = json.loads(event.get('body','{}'))
    if 'username' not in body or 'password' not in body:
        return {
        'statusCode': 400,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': 'Error username o passwd no definido'
        }
        
    conn = pymysql.connect(db_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()
    
    response = None
    
    if cursor.execute("select * from usuarios where nombre_usuario = %s", (body.get("username"),)):
        x=cursor.fetchone()
        response = {
            "id" : x[0], 
            "username" : x[1],
            "correo" : x[2],
            "password" : x[3],
            "recover_password" : x[4],
            "avatar" : x[5],
            "biografia" : x[6]
        }
        if body.get("password") != x[3] :
            response = None
            
        
    cursor.close()
    conn.close()
    
    if response : 
        return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(response)
        }
    
    return {
        'statusCode': 400,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': 'Error user no encontrado o contraseña incorrecta'
        }