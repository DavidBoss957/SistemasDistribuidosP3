import json
import pymysql
import traceback

# Database configuration - replace with your actual details
rds_endpoint = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

def lambda_handler(event, context):
    # Headers for CORS and JSON response
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',  # Adjust if needed for security
        'Access-Control-Allow-Methods': 'OPTIONS,POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Safely handle CORS preflight
    http_method = event.get('httpMethod', '')
    if http_method == 'OPTIONS':
        return {'statusCode': 204, 'headers': headers, 'body': ''}

    try:
        # Connect to the database
        conn = pymysql.connect(
            host=rds_endpoint,
            user=db_username,
            password=db_password,
            db=db_name,
            connect_timeout=5,
            cursorclass=pymysql.cursors.DictCursor
        )

        # Assume body contains JSON with user_id, nombre_usuario, email, biografia
        body = json.loads(event.get("body", "{}"))
        user_id = body.get('userId')
        nombre_usuario = body.get('nombre_usuario')
        email = body.get('email')
        biografia = body.get('biografia')

        # Update user data in database
        with conn.cursor() as cursor:
            sql = """UPDATE usuarios SET nombre_usuario = %s, correo_electronico = %s, biografia = %s WHERE ID = %s"""
            cursor.execute(sql, (nombre_usuario, email, biografia, user_id))
            conn.commit()

        # Successful execution, return a confirmation message
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'User updated successfully'})
        }

    except Exception as e:
        # Log the error for debugging purposes
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        print(f"Error: {e}")
        print(f"Traceback: {traceback_str}")

        # Return a structured error message
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal Server Error', 'message': str(e), 'trace': traceback_str})
        }
    finally:
        # Clean up, close the database connection
        if conn:
            conn.close()

