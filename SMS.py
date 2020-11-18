import os
from dotenv import load_dotenv, find_dotenv
import smtplib

load_dotenv(find_dotenv())

GMAIL = os.environ.get("GMAIL")
PASSWORD = os.environ.get("PASSWORD")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER")

carriers = {
	'att':    '@mms.att.net',
	'tmobile':' @tmomail.net',
	'verizon':  '@vtext.com',
	'sprint':   '@page.nextel.com'
}

def send(message):
	to_number = PHONE_NUMBER+'{}'.format(carriers['att'])
	auth = (GMAIL, PASSWORD)

	server = smtplib.SMTP( "smtp.gmail.com", 587 )
	server.starttls()
	server.login(auth[0], auth[1])

	server.sendmail(auth[0], to_number, message)