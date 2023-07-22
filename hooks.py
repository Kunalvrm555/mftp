from os import environ as env
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib as smtp
import base64
from dotenv import load_dotenv
import requests
from html2text import html2text
load_dotenv()


def make_text(company):
    text = '%s: %s (%s - %s)' % (company['name'], company['job'],
                                 company['start_date'], company['end_date'])
    return text


def send_email(subject, message, attachment_raw=None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'MFTP <' + env['SENDER_EMAIL'] + '>'
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
        connection.sendmail(msg['From'],
                            env['RECIPIENT_EMAIL'], msg.as_string())
    print("Email sent successfully")

def send_whatsapp(notice):
        notice['text'] = html2text(notice['text'])
        subject = 'Notice: %s - %s' % (notice['subject'], notice['company'])
        message = "*" + subject + "*" + "\n" + notice['text'] + "\n" + notice['time']
        if ('attachment_url') in notice:
            encoded_string = base64.b64encode(notice['attachment_raw'])
            try:
                r = requests.post(env['SEND_FILE_URL'],data={'base64string':encoded_string,'caption':message},stream=True)
                print("Attachment sent", r.status_code)
            except Exception as e:
                print("Attachment not sent")
                print(e)
        else:
            try:
                r = requests.post(env['SEND_MESSAGE_URL'],data={"message":message},verify=False)
                print("Notice sent over whatsapp", r.status_code)
            except Exception as e:
                print("Notice not sent over whatsapp")
                print(e)

def notices_updated(notices):
    for notice in reversed(notices):
        subject = 'Notice: %s - %s' % (notice['subject'], notice['company'])
        message = '<i>(%s)</i>: <p>%s</p><br/><hr/>' % (
            notice['time'], notice['text'])
        attachment_raw = notice['attachment_raw'] if 'attachment_raw' in notice else None
        send_email(subject, message, attachment_raw)
        send_whatsapp(notice)
