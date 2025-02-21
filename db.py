import mysql.connector
from contextlib import contextmanager

# Database configuration details (adjust as necessary)
db_config = {
    'host': '185.232.14.154',   # Your database host
    'user': 'u819702430_Admin',  # Your database username
    'password': 'Root123@.',  # Your database password
    'database': 'u819702430_spm',  # Your database name
}

@contextmanager
def get_db_connection():
    # Create a connection to the database
    connection = mysql.connector.connect(**db_config)
    try:
        yield connection  # Yield connection to be used by the caller
    finally:
        connection.close()  # Ensure the connection is closed when done

