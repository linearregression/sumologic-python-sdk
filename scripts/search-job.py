# Oops not done yet; doesn't work
#
# Submits search job, waits for completion, then prints and emails results.
# Pass the query via stdin.
#
# cat query.sumoql | python search-job.py <accessId/email> <accessKey/password> <fromTime> <toTime>

from email.mime.text import MIMEText
import json
from smtplib import SMTP
import sys
import time

from sumologic import SumoLogic

LIMIT = 42
FROM = 'worker@sumologic.com'
TO = 'yoway@sumologic.com'

args = sys.argv
sumo = SumoLogic(args[1], args[2])
fromTime = args[3]
toTime = args[4]
timeZone = args[5]

delay = 2
q = ' '.join(sys.stdin.readlines())
sj = sumo.search_job(q, fromTime, toTime, timeZone)

status = sumo.search_job_status(sj)
while status['state'] != 'DONE GATHERING RESULTS':
	if status['state'] == 'CANCELLED':
		break
	time.sleep(delay)
	delay *= 2
	status = sumo.search_job_status(sj)

print status

if status['state'] == 'DONE GATHERING RESULTS':
	count = status['recordCount']
	limit = count if count < LIMIT else LIMIT # compensate bad limit check
	r = sumo.search_job_records(sj, limit=limit)
	print r
	msg = MIMEText(json.dumps(r))
	msg['From'] = FROM
	msg['To'] = TO
	msg['Subject'] = 'Search Jobs Results'
	smtp = SMTP('localhost')
	smtp.sendmail(FROM, [TO], msg.as_string())
	smtp.quit()
