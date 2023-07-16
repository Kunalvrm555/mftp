from erp import req_args
from os import environ as env
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib as smtp
from dotenv import load_dotenv
load_dotenv()


def make_text(company):
    text = '%s: %s (%s - %s)' % (company['name'], company['job'],
                                 company['start_date'], company['end_date'])
    return text


def send_email(subject, message, attachment_raw=None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = env['SENDER_EMAIL']
    msg['To'] = env['RECIPIENT_EMAIL']
    html_message = f"""
    <html>
        <body>
            <p>{message}</p>
        </body>
    </html>
    """
    msg.attach(MIMEText(html_message, 'html'))
    
    # Attach the file if given
    if attachment_raw is not None:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_raw)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='attachment.pdf')
        msg.attach(part)

    with smtp.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.login(env['SENDER_EMAIL'], env['SENDER_PASSWORD'])
        connection.sendmail(env['SENDER_EMAIL'],
                            env['RECIPIENT_EMAIL'], msg.as_string())
    print("Email sent successfully")


def notices_updated(notices):
    for notice in notices:
        subject = 'Notice: %s - %s' % (notice['subject'], notice['company'])
        message = '<i>(%s)</i>: <p>%s</p><br/><hr/>' % (
            notice['time'], notice['text'])
        attachment_raw = notice['attachment_raw'] if 'attachment_raw' in notice else None
        send_email(subject, message, attachment_raw)
