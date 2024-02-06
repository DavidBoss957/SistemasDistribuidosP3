import json
import pymysql

# Configuración de la conexión a la base de datos
db_host = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'


def lambda_handler(event, context):
    
    body = json.loads(event.get('body','{}'))
    if 'username' not in body or 'password' not in body or 'mail' not in body or 'frase' not in body:
        return {
        'statusCode': 400,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': 'Error, compruebe los campos e intentelo de nuevo'
        }
        
    conn = pymysql.connect(db_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()
    print(body.get("user"))
    response = False;
    print ( (body.get("username"),body.get("mail"), body.get("password"), body.get("frase")));
    try :
        if cursor.execute("insert into usuarios values( NULL,'"+ body.get("username")+"','"+body.get("mail")+"','"+ body.get("password")+"','" + body.get("frase")+"',' ',' ',' ')" ):
            response = True
            conn.commit()
            
    except Exception as error :
        print(error)
        
    cursor.close()
    conn.close()
    
    if response : 
        return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': 'Se ha creado el usuario'
        }
    
    return {
        'statusCode': 400,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': 'Usuario no registrado'
        }