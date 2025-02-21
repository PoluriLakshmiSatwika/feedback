import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MySQL credentials from environment variables
db_host = os.getenv('127.0.0.1')
db_user = os.getenv('system')
db_password = os.getenv('root')
db_name = os.getenv('spm')

# Connect to MySQL
connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

# Check if the connection is successful
if connection.is_connected():
    print(f"Connected to {db_name} at {db_host}")
else:
    print("Failed to connect")

connection.close()
