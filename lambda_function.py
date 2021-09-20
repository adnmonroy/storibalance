import json
import urllib
import hashlib
import datetime
import boto3
import psycopg2
import psycopg2.extras
from botocore.exceptions import ClientError

DS_HOST = "stori.c2ov6qt7ncp7.us-east-1.rds.amazonaws.com"
DS_USER = "root"
DS_DB = "stori"
DS_SCHEMA = "public"
DS_PWD = "Stori123!"
DS_PORT = 5432

SENDER = "Stori Automated Balance <adn.monroy@almendralaser.com>"

#ToDo: Assign user account by database
RECIPIENT = "adn.monroy@gmail.com"
idUsr = 1

AWS_REGION = "us-west-1"
SUBJECT = "Stori Account Balance"
BODY_TEXT = ("Total Balance is: %s\t\tAverage debit amount: %s\r\n\t\t\t\tAverage credit amount: %s\r\n%s")
BODY_HTML = """<html>
<head></head>
<body>
  <center>
  <img width="150" src="https://www.finsmes.com/wp-content/uploads/2020/02/Stori_Logo-300x94.jpg" />
  <h1>BALANCE REPORT</h1>
  <table border="0" spacing="6">
	<tr><td>Total Balance is</td><td>%s</td><td>&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Average debit amount:</td><td>%s</td></tr>
	<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Average credit amount:</td><td>%s</td></tr>
	<tr><td colspan="5"><span style="text-align:left">%s</span></td></tr>
  </table>
  </center>
</body>
</html>
			"""

CHARSET = "UTF-8"

ses = boto3.client('ses')
s3 = boto3.client('s3')
def lambda_handler(event, context):
	#print("Received event: " + json.dumps(event, indent=2))
	sResult = ""
	# Get the object from the event and show its content type
	s3Bucket = event['Records'][0]['s3']['bucket']['name']
	s3Key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding=CHARSET)
	sTEXT = ""
	sHTML = ""
	try:
		oFile = s3.get_object(Bucket=s3Bucket, Key=s3Key)
		sText = oFile['Body'].read().decode(CHARSET)
	except Exception as e:
		print(e)
		print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(s3Key, s3Bucket))
		raise e
		
	bText = bytes(sText, CHARSET)
	sTextKey = hashlib.md5(bText).hexdigest()
	ts = datetime.datetime.now().microsecond
	cursor = None
	try:
		conn = connect2db()
		cursor = conn.cursor()
		sSQL = "SELECT * FROM session WHERE hash = %s"
		cursor.execute(sSQL, (sTextKey,))
		nLen = cursor.rowcount
		if nLen > 0:
			sResult ='{"Result":"OK","Code":2,"Message:"File already processed"}'
			return sResult
		else:
			sSQL = "INSERT INTO session (hash,ts) VALUES (%s,%s)"
			cursor.execute(sSQL,(sTextKey,ts))
	except Exception as e:
		print(e)
		print('Error connecting database. Please check parameters')
		raise e
		
	aText = sText.splitlines()
	fBalance = 0.0
	fDebit = 0.0
	nDebit = 0
	fCredit = 0.0
	nCredit = 0
	dctMonth = {}
	
	for sLine in aText[1:]:
		aFields = sLine.split(',')
		sId = aFields[0]
		sDate = aFields[1]
		aDate = sDate.split('/')
		nMonth = int(aDate[0])
		nDay = int(aDate[0])
		sMonth = datetime.date(1900, nMonth, 1).strftime('%B')
		if sMonth in dctMonth:
			dctMonth[sMonth] = dctMonth[sMonth] + 1
		else:
			dctMonth[sMonth] = 1
		sTrans = aFields[2]
		fTrans = float(sTrans)
		idOperation = 0
		if fTrans<0:
			fDebit = fDebit + fTrans
			nDebit = nDebit + 1
			idOperation = 1
		else:
			fCredit = fCredit + fTrans
			nCredit = nCredit + 1
			idOperation = 2
		sSQL = "INSERT INTO balance (iduser,idoperation,ts,amount) VALUES (%s,%s,%s,%s)"
		cursor.execute(sSQL, (idUsr,idOperation,ts,fTrans))
	conn.commit()
	cursor.close()
	conn.close()
	
	fBalance = fDebit + fCredit
	fAvgDebit = fDebit/nDebit
	fAvgCredit = fCredit/nCredit
	sBalance = "{:>10}".format("{:,.2f}".format(fBalance))
	sAvgDebit = "{:>10}".format("{:,.2f}".format(fAvgDebit))
	sAvgCredit = "{:>10}".format("{:,.2f}".format(fAvgCredit))
	sMonthTransactionsText = ""
	sMonthTransactionsHTML = ""
	
	for sMonth in dctMonth:
		sTimes = str(dctMonth[sMonth])
		sMonthTransactionsText = sMonthTransactionsText + "Number of transcactions in " + sMonth + ": " + sTimes + "\r\n"
		sMonthTransactionsHTML = sMonthTransactionsHTML + "Number of transcactions in " + sMonth + ": " + sTimes + "<br/>"
		
	sHTML = BODY_HTML % (sBalance,sAvgDebit,sAvgCredit,sMonthTransactionsHTML)
	sTEXT = BODY_TEXT % (sBalance,sAvgDebit,sAvgCredit,sMonthTransactionsText)
	try:
		response = ses.send_email(Destination={'ToAddresses': [RECIPIENT,],},Message={'Body': {'Html': {'Charset': CHARSET,'Data': sHTML,},'Text': {'Charset': CHARSET,'Data': sTEXT,},},'Subject': {'Charset': CHARSET,'Data': SUBJECT,},},Source=SENDER,)
	except ClientError as e:
		print(e.response['Error']['Message'])
	else:
		sResult ='{"Result":"OK","Code":1,"Message:"Email sent! Message ID:'+str(response['MessageId']) + '"}'
		return sResult
		
	return False
	

def connect2db():
	conn = psycopg2.connect(database=DS_DB, user=DS_USER, password=DS_PWD, host=DS_HOST, port=DS_PORT,cursor_factory=psycopg2.extras.DictCursor)
	cursor = conn.cursor()
	cursor.execute("SET search_path TO " + DS_SCHEMA)
	conn.commit()
	cursor.close()
	return conn
