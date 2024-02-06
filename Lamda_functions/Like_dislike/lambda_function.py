import json
import pymysql

# Configuration for the database connection
db_host = '44.205.178.122'
db_username = 'twitter'
db_password = 'twitter'
db_name = 'twitter'

bucketUrl = "https://david.sanchez2.2023.s3.us-east-1.amazonaws.com/"

def lambda_handler(event, context):
    # Parse the JSON body from the event
    body = json.loads(event.get('body', '{}'))
    
    # Check if the request has all the required fields
    if 'tweetId' not in body or 'userId' not in body or 'action' not in body:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps('Error: Missing required fields.')
        }
    
    tweet_id = body['tweetId']
    user_id = body['userId']
    action = body['action']  # 'like' or 'dislike'

    # Connect to the database
    conn = pymysql.connect(host=db_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()

    try:
        if action == 'like':
            # Add a like
            cursor.execute("INSERT INTO likes (mensaje_id, usuario_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id=id", (tweet_id, user_id))
        elif action == 'dislike':
            # Remove a like
            cursor.execute("DELETE FROM likes WHERE mensaje_id = %s AND usuario_id = %s", (tweet_id, user_id))
        
        # Commit the transaction
        conn.commit()
        response = 'Action successfully completed.'
        status_code = 200
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        response = json.dumps(f'Error: {e}')
        status_code = 500
    except Exception as e:
        print(f"Error: {e}")
        response = json.dumps(f'Error: {e}')
        status_code = 500
    finally:
        cursor.close()
        conn.close()

    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': response
    }
