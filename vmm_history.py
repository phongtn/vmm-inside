import requests
import datetime
from dash import Dash, html
import dash_mantine_components as dmc
import pandas as pd
from flask import request
from component import col_table

external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

header_response = {'Content-Type': 'application/json; charset=utf-8'}
all_participants = []
finisher = {}
today = datetime.date.today()

def find_finisher_time():
    contest = {100: '#1_100km Ultra', 70: '#1_70km Ultra', 42: '#1_42km', 21: '#1_21km', 15: '#1_15km', 10: '#1_10km'}
    url_get_finisher_2022 = 'https://my1.raceresult.com/163116/RRPublish/data/list?key=c44dcccd62944fa3215da6b7de0cda77&listname=Result%20Lists%7C1.Finisher%20List%20(Ngot)&page=results&contest='
    for ck in contest.keys():
        url_data = url_get_finisher_2022 + str(ck)
        raw_data = requests.get(url_data).json()['data'][contest[ck]]
        # finisher[ck] = raw_data
        for item in raw_data:
            # print(item[0] +' '+ item[3])
            finisher[item[0]] = item[3]    
    return finisher

def prepare_data():    
    find_finisher_time()

    contest_btc = ['#2_100km Ultra', '#3_10km', '#4_15km', '#5_21km', '#6_42km', '#7_70km Ultra']
    participants_2022 = 'https://my1.raceresult.com/163116/RRPublish/data/list?key=c44dcccd62944fa3215da6b7de0cda77&listname=Participants%7CParticipants%20List%20123&page=participants&contest=0&r=all&l=0'
    
    ## prepare all participants data
    raw_data = requests.get(participants_2022).json()['data']
    for c in contest_btc:
         for raw_participant in raw_data[c]:
             strContest = c.split('_')[1]

             # fix missing data   
             if (raw_participant[0] == '5152'):
                 raw_participant[5] = 'Female under 20'

             arr_age_group = raw_participant[5].split(' ')
             age_group = ''
             if (len(arr_age_group) == 2):
                 age_group = arr_age_group[1]
             elif(len(arr_age_group) > 2):
                 age_group = arr_age_group[1].replace('under', '< ') + arr_age_group[2]
             
             participant = list(raw_participant) 
             # to remove duplicated BIB
             participant.pop(2)
             participant.insert(0, strContest)
             participant[5] = age_group
             # check time
             if participant[1] in finisher:
                 participant.append(finisher[participant[1]])
                 participant.append('Finish')
             else:
                 participant.append('0')
                 participant.append('DNF')
                 

             all_participants.append(participant)    

    ## prepare finisher data


    df = pd.DataFrame(all_participants, columns=['Distance', 'BIB', 'Name', 'Gender', 'Birth', 'AG', 'Club', 'Result', 'Status'])
    df['Age'] = today.year - df['Birth'].astype(int)        
    return df

# df = prepare_data()
df = pd.read_csv('history/result2022.csv', index_col=0)
# df.to_csv('result2022.csv', index=False)
app.layout = dmc.Container([html.Div(col_table(df))], fluid=True)

## build api for test
@server.route('/data', methods=['GET'])
def data_contest():
    # data_response = df.head(10).to_json()
    return all_participants, header_response

if __name__ == '__main__':
    app.run_server(debug=True)
