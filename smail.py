import smtplib
import time
import pandas
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

def sendemail(df):
    fromaddr = "`hostname`@company.com"
    toaddr=["security@company.com","network@company.com"]
    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = ",".join(toaddr)
    msg['Subject'] = "IPAM reports subnet change"

    body1 = "  : \n\n "
    body2= "In the attached document, the history of gaps is presented. In the below table, the change detected by the Query today.\n There have been \n\n Kindly,\n Security Engineering."
    msgdf= """\
<html>
  <head></head>
  <body>
  **Info collected from IPAM -- Summary of changes in IPAM**
    {0}
  </body>
</html>
""".format(df.to_html(index=False))

    msg.attach(MIMEText(msgdf,'html'))

    server = smtplib.SMTP('Mail Server IP') #, corp mail server
    server.starttls()
    #server.login(fromaddr, none)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
