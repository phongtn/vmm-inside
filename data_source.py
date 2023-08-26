import country_converter as coco
import datetime
import pandas as pd
import datetime
import requests

# URL to fetch the JSON data from
url_all_contest_2023 = "https://my1.raceresult.com/231112/RRPublish/data/list?key=fb210544f9e10078aca7ea17ad42586f&listname=Participants%7CParticipants%20List%20123&page=participants&contest=0&r=all&l=0"
data_2023 = {}

def fetch_data(year=2023, contest="#all"):
     if int(year) == 2023:
          response = requests.get(url_all_contest_2023)
          if response.status_code == 200:
               data_2023 = response.json()
          else:
            print("Error: Failed to retrieve JSON data of 2023. Status code:", response.status_code)

        
