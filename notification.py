import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send_notification(subject, recipient, body_text):
    host = "smtp.gmail.com"
    sender = "ksu.est.adm@gmail.com"
    system_message = MIMEText(body_text, 'plain', 'utf-8')
    system_message['Subject'] = Header(subject, 'utf-8')
    server = smtplib.SMTP(host, 587)
    server.starttls()
    server.login('ksu.est.adm@gmail.com','ovkuhhqofncmkxso')
    server.sendmail(sender, [recipient], system_message.as_string())
    server.quit()