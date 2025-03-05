import smtplib
from email.message import EmailMessage
import codecs
import logging

from app.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_FROM

HTMLFile = codecs.open("user/mail_template.html", 'r', "utf-8").read()
HTMLFileInvite = codecs.open("user/mail_template_invite.html", 'r', "utf-8").read()

def send_verify_email (user, link):
    content = (f"Thank you, {user.first_name} {user.last_name}, for starting the account creation process. "
               f"To verify your identity, please click the 'Verify Now' button. "
               f"If you do not wish to create an account, you may ignore this message.")

    title = 'Email Verification'
    index = HTMLFile.format(title=title,link=link,content=content, button_text='Verify Now')
    logging.getLogger().error(link) 

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) 
        for email in set([user.email]):
            msg = EmailMessage()
            msg['Subject'] = "Verify Email Account"
            msg['From'] =  EMAIL_FROM
            msg['To'] = email
            msg.set_content(index,subtype='html')
            smtp.send_message(msg)

def send_forgot_password_email(user, link):
    content = (f"Hello, {user.first_name} {user.last_name}, "
               f"We received a request to reset your password. Click the Reset Button or Link given below to reset it. "
               f"If you didn’t request a password reset, please ignore this email.")

    title = 'Forgot Password Email'
    index = HTMLFile.format(title=title, link=link, content=content, button_text='Reset')
    logging.getLogger().error(link)

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        for email in set([user.email]):
            msg = EmailMessage()
            msg['Subject'] = "Forgot Password Email"
            msg['From'] = EMAIL_FROM
            msg['To'] = email
            msg.set_content(index,subtype='html')
            smtp.send_message(msg)
        

def send_invite_email (email, link, groupName):
    content = f"We want to invite you to our group {groupName}. Please enter the following verification code when prompted. If you don’t want to, you can ignore this message."
    title = 'Group Invitation'
    index = HTMLFileInvite.format(title=title,link=link,content=content)
    logging.getLogger().error(link) 
    
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) 
        for email in set([email]):
            msg = EmailMessage()
            msg['Subject'] = "Group Invitation"
            msg['From'] = EMAIL_FROM
            msg['To'] = email
            msg.set_content(index,subtype='html')
            smtp.send_message(msg)
        
