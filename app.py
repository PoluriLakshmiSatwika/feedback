from flask import Flask,redirect,url_for,request,render_template,flash,session,Response
import mysql.connector
from email.message import EmailMessage
from key import secret_key,salt
from itsdangerous import URLSafeTimedSerializer
from stoken import token
from cmail import sendmail
import os
import smtplib
import pandas as pd
from flask import Flask, render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector  # Import the MySQL library
from sotp import *
from tokenreset import token
import csv
import io
import logging


# Replace 'your-secret-key' with your actual secret key

app=Flask(__name__)
app.secret_key= b'\x011\xd3\xb9\x1a\x97{\xe6\x87\xeb{2\xbe*\xcfI\xde\x02\xe7\x89'
app.config['SESSION_TYPE']='filesystem' 
user=os.environ.get('RDS_USERNAME')
db=os.environ.get('RDS_DB_NAME')
password=os.environ.get('RDS_PASSWORD')
host=os.environ.get('RDS_HOSTNAME')
port=os.environ.get('RDS_PORT')
with mysql.connector.connect(host="Satwika",user="system",password="root",port="3306",db="spm") as conn:
    cursor=conn.cursor(buffered=True)
    #cursor.execute("create table if not exists users(rollno varchar(50) primary key,password varchar(15),email varchar(60))")
    #cursor.execute("CREATE TABLE contact (name varchar(255) NOT NULL,email varchar(255) NOT NULL,message varchar(255) NOT NULL)");
    #cursor.execute("CREATE TABLE sur_data (name VARCHAR(255) NOT NULL,rollno VARCHAR(255) NOT NULL,email VARCHAR(255) NOT NULL,dept VARCHAR(255) NOT NULL,specialization VARCHAR(255) NOT NULL,one VARCHAR(255) NOT NULL,two VARCHAR(255) NOT NULL,three VARCHAR(255) NOT NULL,four VARCHAR(255) NOT NULL,five VARCHAR(255) NOT NULL,six VARCHAR(255) NOT NULL,seven VARCHAR(255) NOT NULL,eight VARCHAR(255) NOT NULL,nine VARCHAR(255) NOT NULL,ten VARCHAR(255) NOT NULL,eleven VARCHAR(255) NOT NULL,twelve VARCHAR(255) NOT NULL,thirteen VARCHAR(255) NOT NULL,fourteen VARCHAR(255) NOT NULL,fifteen VARCHAR(255) NOT NULL,sixteen VARCHAR(255) NOT NULL,seventeen VARCHAR(255) NOT NULL,eighteen VARCHAR(255) NOT NULL,nineteen VARCHAR(255) NOT NULL)");
    cursor.close()
mydb=mysql.connector.connect(host="Satwika",user="system",password="root",db="spm")
serializer = URLSafeTimedSerializer(b'\x011\xd3\xb9\x1a\x97{\xe6\x87\xeb{2\xbe*\xcfI\xde\x02\xe7\x89')
db_config = {
    "host": "Satwika",
    "user": "system",
    "password": "root",
    "database": "spm",
}

# Attempt to establish a database connection
try:
    # Create a database connection
    db_connection = mysql.connector.connect(**db_config)

    # Check if the connection was successful
    if db_connection.is_connected():
        logging.info("Database connection established successfully!")

except mysql.connector.Error as e:
    # Handle the error if the connection fails
    logging.error(f"Error connecting to the database: {e}")

# Close the database connection when you're done
if 'db_connection' in locals():
    db_connection.close()
try:
    # Create a database connection
    db_connection = mysql.connector.connect(**db_config)

    # Check if the connection was successful
    if db_connection.is_connected():
        print("Database connection established successfully!")

except mysql.connector.Error as e:
    # Handle the error if the connection fails
    print(f"Error connecting to the database: {e}")
if mydb.is_connected():
    cursor = mydb.cursor(buffered=True)
else:
    flash('Database connection lost')

# Close the database connection when you're done
if 'db_connection' in locals():
    db_connection.close()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home',methods=['GET','POST'])
def home():
    return render_template('home.html')
def create_smtp_server():
    server = smtplib.SMTP('smtp.gmail.com', 465)
    server.starttls()
    return server


# The rest of your routes...
def generate_token(data):
    return serializer.dumps(data)

def verify_token(token, max_age):
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except Exception as e:
        # Handle token verification error here
        return None
def send_confirmation_email(email, body):
    try:
        # Use SMTP_SSL with port 465 for SSL
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("satwikapoluri@gmail.com", "mrlq kqqg umdy nunb")  # Use your app-specific password here
        
        # Create the email message
        msg = EmailMessage()
        msg['From'] = "satwikapoluri@gmail.com"
        msg['To'] = email
        msg['Subject'] = 'Email Confirmation'
        msg.set_content(body)

        # Send the email
        server.send_message(msg)
        logging.info("Email sent successfully!")
        
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise  # Re-raise the exception to handle it in your main function
    
    finally:
        # Ensure the SMTP connection is closed
        try:
            if server:
                server.quit()
                logging.info("SMTP connection closed.")
        except NameError:
            logging.warning("Server object was not created.")
        except Exception as e:
            logging.error(f"Error closing SMTP connection: {e}")

        server.quit()

from mysql.connector import pooling, Error


# Database connection pool
db_config = {
    "host": "Satwika",
    "user": "system",
    "password": "root",
    "database": "spm",
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

# Environment variable for email password
EMAIL_PASSWORD = os.getenv('mrlq kqqg umdy nunb')  # Set this in your environment

def get_db_connection():
    """Retrieve a database connection from the pool."""
    try:
        return connection_pool.get_connection()
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        flash("Database connection error")
        return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        rollno = request.form['rollno']
        password = request.form['password']
        email = request.form['email']
        cursor = None

        try:
            # Check database connection
            if not mydb.is_connected():  # Check if the connection is active
                mydb.reconnect()  # Reconnect if the connection is lost
            
            cursor = mydb.cursor(buffered=True)
            
            # Check if rollno already exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE rollno=%s', [rollno])
            count = cursor.fetchone()[0]
            
            # Check if email already exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE email=%s', [email])
            count1 = cursor.fetchone()[0]

        except mysql.connector.Error as e:
            # Log database connection error
            app.logger.error(f"Database error: {e}")
            flash('Database connection error')
            return render_template('register.html')
        
        finally:
            if cursor:  # Only close the cursor if it was initialized
                cursor.close()

        # Check for duplicate rollno or email
        if count == 1:
            flash('Username already in use')
            return render_template('register.html')
        elif count1 == 1:
            flash('Email already in use')
            return render_template('register.html')

        # Generate token for email verification
        data = {'rollno': rollno, 'password': password, 'email': email}
        token_url = url_for(
            'confirm',
            token=token(data, salt='f4db28e23409f84183ba442b7d607d6d'),
            _external=True
        )

        # Email setup
        subject = 'Email Confirmation'
        body = f"Thanks for signing up\n\nFollow this link to complete registration: {token_url}"

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login("satwikapoluri@gmail.com", "mrlq kqqg umdy nunb")  # Use app-specific password
                msg = MIMEMultipart()
                msg['From'] = "satwikapoluri@gmail.com"
                msg['To'] = email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server.sendmail("satwikapoluri@gmail.com", email, msg.as_string())
        
        except Exception as e:
            flash('Error sending confirmation email')
            app.logger.error(f"Error sending email: {e}")  # Log error for debugging
            return render_template('register.html')
        
        flash('Confirmation link sent to your email')
        return redirect(url_for('login'))
    
    return render_template('register.html')


'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        rollno = request.form['rollno']
        password = request.form['password']
        email = request.form['email']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT COUNT(*) FROM users WHERE rollno=%s', [rollno])
        count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM users WHERE email=%s', [email])
        count1 = cursor.fetchone()[0]
        cursor.close()
        
        if count == 1:
            flash('Username already in use')
            return render_template('register.html')
        elif count1 == 1:
            flash('Email already in use')
            return render_template('register.html')
        
        data = {'rollno': rollno, 'password': password, 'email': email}
        subject = 'Email Confirmation'
        body = f"Thanks for signing up\n\nfollow this link for further steps-{url_for('confirm', token=token(data, salt='f4db28e23409f84183ba442b7d607d6d'), _external=True)}"

        try:
            # Directly create the SMTP_SSL connection
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login("satwikapoluri@gmail.com", "mrlq kqqg umdy nunb")  # Use your app-specific password here
                msg = MIMEMultipart()
                msg['From'] = "satwikapoluri@gmail.com"
                msg['To'] = email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server.sendmail("satwikapoluri@gmail.com", email, msg.as_string())
                
        except Exception as e:
            flash('Error sending confirmation email')
            print(f"Error sending email: {e}")  # Print error for debugging
            return render_template('register.html')
        
        flash('Confirmation link sent to your email')
        return redirect(url_for('login'))
    
    return render_template('register.html')

'''


        
@app.route('/reset/<email>', methods=['GET', 'POST'])
def reset(email):
    if request.method == 'POST':
        newpassword = request.form['npassword']
        confirmpassword = request.form['cpassword']
        # Password validation
        if newpassword == confirmpassword:
            try:
                # Initialize the cursor
                cursor = mydb.cursor(buffered=True)

                # Update the password for the user associated with the email
                cursor.execute('UPDATE users SET password=%s WHERE email=%s', [newpassword, email])

                # Check if any rows were affected (updated)
                row_count = cursor.rowcount
                logging.info("Row Count:", row_count)
                mydb.commit()

                if row_count > 0:
                    flash('Password reset successful. Please log in with your new password.')
                    return redirect(url_for('login'))
                else:
                    flash('No rows updated in the database. Please contact support.')
                    return render_template('newpassword.html')

            except Exception as e:
                logging.error(f"Error updating password: {e}")
                flash('An error occurred while updating the password. Please try again.')
                return render_template('newpassword.html')

            finally:
                if 'cursor' in locals():  # Check if cursor was initialized
                    cursor.close()

        else:
            flash('Passwords do not match. Please try again.')
            return render_template('newpassword.html')

    return render_template('newpassword.html')


@app.route('/forget', methods=['GET', 'POST'])
def forget():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if the email is valid (you can add more validation here)
        if not email or '@' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('forgot.html')

        # Check if the database connection is available
        if not mydb.is_connected():
            try:
                # Reconnect if connection is lost
                mydb.reconnect(attempts=3, delay=5)
            except mysql.connector.errors.OperationalError as e:
                flash('Database connection is not available. Please try again later.', 'error')
                return render_template('forgot.html')
        
        try:
            cursor = mydb.cursor(buffered=True)
            
            # Check if the email exists in the database
            cursor.execute('SELECT count(*) FROM users WHERE email = %s', [email])
            count = cursor.fetchone()[0]

            if count == 1:
                # Fetch the email from the database
                cursor.execute('SELECT email FROM users WHERE email = %s', [email])
                email_result = cursor.fetchone()[0]

                # Generate the reset link with email instead of token
                subject = 'Forget Password'
                reset_link = url_for('reset', email=email_result, _external=True)
                body = f"Use this link to reset your password:\n\n{reset_link}"

                # Send the email (ensure sendmail is defined properly)
                sendmail(to=email_result, body=body, subject=subject)
                flash('Reset link sent, check your email', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid email id', 'error')
                return render_template('forgot.html')

        except Exception as e:
            logging.error(f"Error occurred: {e}")  # You can replace this with logging
            flash('An error occurred while processing your request. Please try again.', 'error')
            return render_template('forgot.html')

        finally:
            if cursor:
                cursor.close()

    return render_template('forgot.html')



@app.route('/confirm/<token>')
def confirm(token):
    try:
        # Deserialize the token with a time limit of 24 hours (86400 seconds)
        serializer = URLSafeTimedSerializer(secret_key)
        data = serializer.loads(token, salt='f4db28e23409f84183ba442b7d607d6d', max_age=86400)
    except Exception as e:
        logging.error(f"Token error: {e}")
        return 'Link expired. Please register again.', 400

    # Ensure the MySQL connection is active
    global mydb
    try:
        # Check if mydb is None or the connection is not available
        if mydb is None or not mydb.is_connected():
            mydb = mysql.connector.connect(
                host="Satwika",
                user="system",
                password="root",
                database="spm"
            )
        
        cursor = mydb.cursor(buffered=True)
        rollno = data['rollno']

        # Check if the user is already registered
        cursor.execute('SELECT COUNT(*) FROM users WHERE rollno = %s', [rollno])
        count = cursor.fetchone()[0]

        if count == 1:
            cursor.close()
            flash('You are already registered!')
            return redirect(url_for('login'))
        
        # Register the new user
        cursor.execute(
            'INSERT INTO users (rollno, password, email) VALUES (%s, %s, %s)',
            [data['rollno'], data['password'], data['email']]
        )
        mydb.commit()
        cursor.close()

        flash('Details registered successfully!')
        return redirect(url_for('login'))

    except mysql.connector.Error as e:
        logging.error(f"Database error: {e}")
        return "Internal Server Error", 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "An error occurred. Please try again.", 500

        
@app.route('/dashboard')
def dashboard():
    if session.get('user'):
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')    

import re

@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Basic form validation
        if not name or not email or not message:
            flash('All fields are required.')
            return render_template('contactus.html')

        # Validate email format
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, email):
            flash('Please enter a valid email address.')
            return render_template('contactus.html')

        try:
            cursor = mydb.cursor(buffered=True)
            
            # Insert the contact message into the database
            cursor.execute('INSERT INTO contact (name, email, message) VALUES (%s, %s, %s)', (name, email, message))
            mydb.commit()  # Commit the transaction to save the data
            
            flash('Your message has been successfully sent!')
            
        except Exception as e:
            logging.error(f"Error inserting contact message: {e}")
            flash('There was an issue sending your message. Please try again later.')
        
        finally:
            cursor.close()
        
        return redirect(url_for('index'))
        
    return render_template('contactus.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect(url_for('dashboard'))  # Redirect to the dashboard if already logged in

    # Ensure a valid database connection
    try:
        if not mydb.is_connected():
            mydb.connect()  # Reconnect if not connected
        cursor = mydb.cursor(buffered=True)
        
        if request.method == 'POST':
            rollno = request.form['rollno']
            password = request.form['password']

            # Query the database for the user
            cursor.execute('SELECT count(*) from users where rollno=%s and password=%s', [rollno, password])
            count = cursor.fetchone()[0]

            if count == 1:
                session['user'] = rollno
                flash('Login successful')
                return redirect(url_for('dashboard'))  # Redirect to the dashboard or home page
            else:
                flash('Invalid username or password')

    except mysql.connector.Error as err:
        flash(f"Error: {err}")
    finally:
        # Ensure the cursor is closed after the query
        cursor.close()
    
    return render_template('login.html')


@app.route('/logout')

def logout():
    if session.get('user'):
        session.pop('user')
        flash('Successfully logged out')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    




@app.route('/survey', methods=['GET', 'POST'])
def survey_start():
    if request.method == 'POST':
        name = request.form['name']
        rollno = request.form['rollno']
        email = request.form['email']
        dept = request.form['dept']
        specialization = request.form['specialization']
        one = request.form['one']
        two = request.form['two']
        three = request.form['three']
        four = request.form['four']
        five = request.form['five']
        six = request.form['six']
        seven = request.form['seven']
        eight = request.form['eight']
        nine = request.form['nine']
        ten = request.form['ten']
        eleven = request.form['eleven']
        twelve = request.form['twelve']
        thirteen = request.form['thirteen']
        fourteen = request.form['fourteen']
        fifteen = request.form['fifteen']
        sixteen = request.form['sixteen']
        seventeen = request.form['seventeen']
        eighteen = request.form['eighteen']
        nineteen = request.form['nineteen']

        try:
            # Use context manager to manage database connection and cursor
            with get_db_connection() as db_connection:
                if db_connection:
                    cursor = db_connection.cursor(buffered=True)
                    try:
                        cursor.execute(
                            'INSERT INTO sur_data (name, rollno, email, dept, specialization, one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, nineteen) '
                            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                            (name, rollno, email, dept, specialization, one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, nineteen)
                        )
                        db_connection.commit()
                        flash('Survey submitted successfully', 'success')
                        return redirect(url_for('thank_you'))  # Redirect to thank-you page
                    except Exception as e:
                        logging.error(f"Error during insert: {e}")
                        flash('An error occurred while submitting the survey.', 'error')
                    finally:
                        cursor.close()  # Always close the cursor after use
                else:
                    flash('Database connection is lost. Please try again later.', 'error')
        except Exception as e:
            logging.error(f"Error while connecting to database: {e}")
            flash('An error occurred while connecting to the database.', 'error')

    return render_template("survey.html")
def fetch_survey_data():
    cursor = None  # Initialize cursor to None to ensure it's always defined
    try:
        # Use context manager to manage the connection
        with get_db_connection() as db_connection:
            if db_connection:
                cursor = db_connection.cursor(dictionary=True)
                cursor.execute('SELECT * FROM sur_data')  # Replace with your actual SQL query
                survey_data = cursor.fetchall()
                return survey_data
            else:
                logging.info("Database connection is not available.")
                return None
    except Exception as e:
        logging.error(f"Error fetching survey data: {e}")
        return None
    finally:
        if cursor:
            cursor.close()  # Always close the cursor if it was created

@app.route('/download_survey_data', methods=['GET'])
def download_survey_data():
    # Fetch survey data from the database
    survey_data = fetch_survey_data()

    if not survey_data:
        return "No survey data found."

    # Create a buffer to hold the CSV data
    buffer = io.StringIO()

    # Use the CSV module to write the survey data to the buffer
    csv_writer = csv.writer(buffer)
    header = ["name", "rollno", "email", "dept", "specialization", "overall exp", "are prof well trained?", "satified with teaching?", "satisfied with clg facilities", "admission process", "food quality", "fee paying process", "supportive faculty", "extra-curricular activities", "hygine environment", "sports area", "professors support", "computer labs", "library", "joining siblings", "racial biases", "reaction on bullying classes", "overall exp", "own experience"]
    csv_writer.writerow(header)
    for row in survey_data:
        csv_writer.writerow(row.values())

    # Set the appropriate headers for CSV download
    buffer.seek(0)
    return Response(
        buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=survey_data.csv'}
    )

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# main.py
from db import get_db_connection

with get_db_connection() as connection:
    cursor = connection.cursor(buffered=True)
    
    # Query for 'users' table
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(user)
    
    # Query for 'orders' table
    cursor.execute("SELECT * FROM sur_data")
    orders = cursor.fetchall()
    for order in orders:
        print(order)
    
    # Query for 'products' table
    cursor.execute("SELECT * FROM contact")
    products = cursor.fetchall()
    for product in products:
        print(product)

if __name__=='__main__':
    app.run()
