import json
from pathlib import Path
from datetime import date

import smtplib

def update_stats():
	try:
		with open('data.json') as stat_file:
			stats =  json.load(stat_file)
	except FileNotFoundError:
		stats = {
			'week':0,
			'all':0
		}
		with open('data.json','w') as stat_file:
			json.dump(stats,stat_file)
	for stat in stats:
		stats[stat] += 1
	if date.today().weekday() == 0:
		send_stat_mail(stats["week"], stats["all"])
		stats["week"] = 0
	with open('data.json','w') as stat_file:
		json.dump(stats,stat_file)

def send_stat_mail(week, all):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('simmonds.bot@gmail.com','BBQ123bbq')

    subject = f"BBQ Stock Checker Stats"
    body = f"I am still checking!\n\nChecks this week: {week}\nChecks since 20/10/2020: {all}"
    message = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        'simmonds.bot@gmail.com',
        'tim.simmonds1@gmail.com',
        message
    )
    server.quit()

update_stats()