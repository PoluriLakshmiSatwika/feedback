import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = 'smtp.gmail.com'
smtp_port = 465  # SSL port
sender_email = 'satwikapoluri@gmail.com'
sender_password = 'mrlq kqqg umdy nunb'  # Use the App Password you generated
recipient_email = 'amr.21hm1a5922@gmail.com'
subject = 'Test Email'
body = 'This is a successful test email sent via Gmail SMTP.'

try:
    # Create a connection to the SMTP server using SSL
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    
    # Login to your email account
    server.login(sender_email, sender_password)

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the email body as plain text
    message.attach(MIMEText(body, 'plain'))

    # Send the email
    server.sendmail(sender_email, recipient_email, message.as_string())

    # Close the SMTP server connection
    server.quit()

    print("Test email sent successfully")
except Exception as e:
    print(f"Test email sending failed: {str(e)}")
