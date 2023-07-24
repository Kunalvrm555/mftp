from erp import req_args
from os import environ as env
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib as smtp
import base64
import re
from dotenv import load_dotenv
import requests
from html2text import html2text
load_dotenv()


def make_text(company):
    text = '%s: %s (%s - %s)' % (company['name'], company['job'],
                                 company['start_date'], company['end_date'])
    return text


def send_email(subject, notice, attachment_raw=None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'MFTP <' + env['SENDER_EMAIL'] + '>'
    msg['To'] = env['RECIPIENT_EMAIL']
    # Identify the URLs and replace them with 'Click here'
    notice_text = re.sub(r"(https?://[^\s]+)", r'<a href="\1">Click here</a>', notice['text'])

    html_message = f"""
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; width: 90%; margin: 0 auto; border: 1px solid #333; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);">
                <div style="margin-bottom: 20px;">
                    {notice_text}
                </div>
                <div style="text-align: right; font-style: italic;">
                    ({notice['time']})
                </div>
            </div>
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

def clean_links(text):
    text = re.sub(r'-\s', '-', text)  # remove whitespace that follows a hyphen
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    for url in urls:
        clean_url = url.replace("\n", "")
        text = text.replace(url, clean_url)
    return text

def send_whatsapp(notice):
        notice_text = html2text(notice['text'])
        notice_text = clean_links(notice_text)
        subject = '*Notice: %s - %s*\n' % (notice['subject'], notice['company'])
        message = subject + "\n" + notice_text + "\n" + notice['time']
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
        attachment_raw = notice['attachment_raw'] if 'attachment_raw' in notice else None
        send_email(subject, notice, attachment_raw)
        send_whatsapp(notice)
