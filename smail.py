import smtplib
import time
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
 
def sendemail():
    fromaddr = "`hostname`@securekey.com"
    toaddr = ["securityteam@company.com", "networkteam@company.com"] #
    msg = MIMEMultipart()
 
    msg['From'] = fromaddr
    msg['To'] = ",".join(toaddr)
    msg['Subject'] = "Change in corporate VLAN"
 
    body = "  You receive this email because VLAN(s) have been deleted and/or added in the last 7 days.\n\n In the attached document, the history of gaps is presented\n see the lines corresponding to today to see changes. \n\n Kindly,\n Security Engineering."
 
    msg.attach(MIMEText(body, 'plain'))
 
    file = "gap.csv"
    attachment = open("gap.csv", "rb")
 
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename= file)
 
    msg.attach(part)
 
    server = smtplib.SMTP('<mail-server-IP@>') #, corp mail server
    server.starttls()
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
