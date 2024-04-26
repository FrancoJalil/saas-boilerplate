
from email.mime.text import MIMEText
from django.template import Template, Context
import smtplib
from email.message import EmailMessage

from email.mime.multipart import MIMEMultipart
import os


def send_email(email_format, to_email, context={}):
    # Create an email message object
    message = MIMEMultipart('alternative')

    sender_email_address = os.environ.get('EMAIL_ADDRESS')
    email_password = os.environ.get('EMAIL_PASSWORD')
    receiver_email_address = to_email

    # Configure email headers

    message['From'] = sender_email_address
    message['To'] = receiver_email_address

    email_subject = ""
    file_content = ""

    if email_format == "register":

        with open('resources/register.html', 'r') as file:
            file_content = file.read()
            email_subject = "Welcome to TestInc!"

    elif email_format == "buy_custom":

        with open('resources/buy-custom.html', 'r') as file:
            file_content = file.read()
            email_subject = "Thank you for purchase Custom Pack!"

    elif email_format == "OTP":
        with open('resources/otp.html', 'r') as file:
            file_content = file.read()
            email_subject = "Confirmation code"

    # Utilizar plantilla de cadena para procesar el contenido HTML con el contexto
    template = Template(file_content)
    file_content_processed = template.render(Context(context or {}))

    message['Subject'] = email_subject
    part1 = MIMEText(file_content_processed, "html")
    # part1 = MIMEText(file_content, "html")

    message.attach(part1)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email_address, email_password)
            server.sendmail(sender_email_address,
                            receiver_email_address, message.as_string())
            return True
    except:
        return False


def send_email_to_me(to, subject, msg):

    if len(subject) <= 0 or len(msg) <= 0:
        return

    # Create an email message object
    message = EmailMessage()

    sender_email_address = os.environ.get('EMAIL_ADDRESS')
    email_password = os.environ.get('EMAIL_PASSWORD')
    receiver_email_address = os.environ.get('EMAIL_ADDRESS')
    # Configure email headers
    message['From'] = sender_email_address
    message['To'] = receiver_email_address

    email_content = f"Subject: {subject} | Msg: {msg}"
    email_subject = f"MSG | {to}"

    message['Subject'] = email_subject
    message.set_content(email_content)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email_address, email_password)
        server.send_message(message)


def send_normal_email(subject, message, to_email):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Puedes usar 465 para SSL
    smtp_username = os.environ.get('EMAIL_ADDRESS')
    smtp_password = os.environ.get('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        server.login(smtp_username, smtp_password)

        server.sendmail(smtp_username, to_email, msg.as_string())

        server.quit()

        return True
    except Exception as e:

        print(f"Failed to send email: {e}")

        return False

