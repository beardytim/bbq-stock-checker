from twilio.rest import Client
import requests
from bs4 import BeautifulSoup
import smtplib
import json
from pathlib import Path
import datetime
import keys

def scrape_data(item):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"}
    page = requests.get(item.URL, headers=headers)
    soup = BeautifulSoup(page.content,'html.parser')

    if(item.site=='bbq'):
        item.title = soup.find("h1", class_='product_title entry-title').get_text()
        item.stock = soup.find("p", class_='stock').get_text()
        item.price = soup.find("p", class_='price').get_text()[:-8]
    elif(item.site=='argos'):
        item.title = soup.find("h2", class_='Namestyles__Main-sc-269llv-1 bojEI').get_text()[:-8]
        item.stock = soup.find("p", class_='CheckStoreBoxstyles__FulfilmentHeading-pzfx58-0 hVmSus').get_text()
        item.price = soup.find("li", class_='Pricestyles__Li-sc-1oev7i-0 haYQtv').get_text()
        if item.stock == 'Currently unavailable':
            item.stock = 'Out of stock'

def send_message(body):
    client = Client(keys.twilio_acccount_sid,keys.twilio_auth_token)
    message = client.messages.create(from_=keys.twilio_from, body=body,to=keys.twilio_to)

def send_mail(subject, body):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(keys.gmail_from,keys.gmail_pass)

    message = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        keys.gmail_from,
        keys.gmail_to,
        message
    )
    server.quit()

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
    if ((datetime.datetime.today().weekday() == 0) and (datetime.datetime.today().hour == 20)):
        week = stats["week"]
        allTime = stats["all"]
        send_mail(f"BBQ Stock Bot Stats", f"I am still checking!\nChecks this week: {week}\nChecks since 21/10/2020: {allTime}")
        stats["week"] = 0
    with open('data.json','w') as stat_file:
        json.dump(stats,stat_file)

class Item:
    def __init__(self, URL, site):
        self.title = ''
        self.stock = ''
        self.price = ''
        self.URL = URL
        self.site = site

items = [Item('https://www.barbequick.com/grillguide/product/57cm-charcoal-kettle-pizza-barbecue/','bbq')]
# Item('https://www.argos.co.uk/product/3417542','argos')
inStock = []

for item in items:
    scrape_data(item)
    if item.stock != 'Out of stock':
        inStock.append(item)
if inStock:
    body = f"Great news!\n"
    for item in inStock:
      body += f"\n{item.title} - {item.stock} - {item.URL} "
    send_mail("STOCK ALERT!", body)
    send_message(body)

update_stats()