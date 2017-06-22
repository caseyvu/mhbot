import smtplib
import mimetypes
from email.utils import COMMASPACE, formatdate
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import os, time

def _send_mail(to, smtp_settings, subject, text, files=[]):
    assert type(to)==list
    assert type(files)==list

    from_addr = smtp_settings['address']
    password = smtp_settings['password']
    server = smtp_settings['server']

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        file_basename = os.path.basename(f)
        ctype, encoding = mimetypes.guess_type(f)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
                
        maintype, subtype = ctype.split("/", 1)
        
        if maintype == "text":
            fp = open(f)
             # Note: we should handle calculating the charset
            attachment = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "image":
            fp = open(f, "rb")
            attachment = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "audio":
            fp = open(f, "rb")
            attachment = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(f, "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename=file_basename)
        attachment.add_header('Content-ID', '<'+file_basename+'>')
        msg.attach(attachment)

    smtp = smtplib.SMTP(server)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(from_addr, password)
    smtp.sendmail(from_addr, to, msg.as_string() )
    smtp.quit()

def send_captcha_alert_mail(to, email_settings, captcha_file):
    subject = "[MouseHunt] Got captcha"
    message = "See attachment. Login to server and enter code"
    _send_mail(to, email_settings, subject, message, files=[captcha_file])

# Test email:
if __name__ == '__main__':
    smtp_settings = dict()
    smtp_settings['server'] = 'smtp.gmail.com:587'
    smtp_settings['password'] = ''
    smtp_settings['address'] = ''
    _send_mail(['vuanhthu888@gmail.com'],smtp_settings,'Test email!','Test email sent from my server')
