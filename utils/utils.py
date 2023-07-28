from config import SENDER_EMAIL, SENDER_PW, RECIPIENTS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, body):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Create SMTP session for sending the mail
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(SENDER_EMAIL, SENDER_PW)
        smtp_server.send_message(msg)
        print(f'Email sent: \n{body}')