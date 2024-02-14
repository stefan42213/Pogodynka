import requests
import re
from datetime import datetime, timedelta
import time
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client["Weather"]
collection = db['Weather']

day = datetime.now().strftime('%d-%m-%Y')
current_time = datetime.now().strftime('%H:%M')


# Class is collecting current temperature and temperature for 4 next days in Fordon, from website www.forcea.pl
class Weather():

    def __init__(self):
        self.link = 'https://www.foreca.pl/Poland/Kujawsko--Pomorskie-Voivodship/Rybaki'
        self.html_text = ""
        self.temp = []

# Collecting html text from website, if we don't have internet connection or website doesn't exists function returns -1 else returns 1
    def getting_html(self):
        try:
            response = requests.get(self.link)
            if response.status_code != 200:
                print("Can't find web")
                return -1
            else:
                self.html_text = response.text
                return 1

        except:
            print(f"No internet connection")
            return -1

# Collectiong current temperature from web and saving it in 2 dims array [date(day-month-year) , temperature]
    def collecting_temp_n(self):
        self.temp = []
        index_b = re.search(r'<span class="value temp temp_c">', self.html_text).end()
        index_e = re.search(r'&deg;', self.html_text[index_b:]).start()
        self.temp.append([self.html_text[index_b: index_b + index_e]])


# Running class every 30 mins if there is no error with getting data , but if there is then wait 5 mins and try again
global set_id 
set_id = 0 
MyWeather = Weather()
while (True):
    if (MyWeather.getting_html() != 1):
        print("There is error , after 5 minutes program will try again to connect with website")
        time.sleep(300)
        continue
    
    MyWeather.collecting_temp_n()
    print(MyWeather.temp)
    print("Waiting 30 mins for next data actualization")
    time.sleep(1)

    set_id += 1
    current_id = set_id  # Assign set_id to current_id
    current_time = datetime.now().strftime('%H:%M')  # Update current_time
    print(f"Current set_id: {current_id}")
    if current_id == 48 or current_time == "00:00": #if id == 48 or local time == 00:00 then delete whole database and start counting over again
        for i in range(48):                         # 00:00 means noon (new day)
            collection.delete_one({"_id": i }) #mogłem zrobić delete_many ({}) ale ciul XD
        set_id = 0   
    input = { "_id":set_id,"day":day,"time":current_time,"temp": MyWeather.temp }
    collection.insert_one(input)
    newvalues = { "$set": { "_id":set_id,"day":day,"time":current_time,"temp": MyWeather.temp } } #updates the dataset with new values
    collection.update_one(input, newvalues)
