import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os, time

def _send_mail(to, fro, subject, text, files=[],server="localhost"):
    assert type(to)==list
    assert type(files)==list


    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
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
        attachment.add_header("Content-Disposition", "attachment", filename=os.path.basename(f))
        attachment.add_header('Content-ID', '<{}>'.format(os.path.basename(f)))
        msg.attach(attachment)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string() )
    smtp.close()

def send_captcha_alert_mail(to, fro, captcha_file):
    subject = "[MouseHunt] Got captcha"
    message = "See attachment. Login to server and enter code"
    _send_mail(to, fro, subject, message, files=[captcha_file])

# Test email:
if __name__ == '__main__':
    _send_mail(['vuanhthu888@gmail.com'],'cat@caseyvu.com','Test email!','Test email sent from my server')
