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


def prepare_data():
    contest = {100: '#1_100km Ultra', 70: '#1_70km Ultra', 42: '#1_42km', 21: '#1_21km', 15: '#1_15km', 10: '#1_10km'}
    contest_btc = ['#2_100km Ultra', '#3_10km', '#4_15km', '#5_21km', '#6_42km', '#7_70km Ultra']
    participants_2022 = 'https://my1.raceresult.com/163116/RRPublish/data/list?key=c44dcccd62944fa3215da6b7de0cda77&listname=Participants%7CParticipants%20List%20123&page=participants&contest=0&r=all&l=0'
    url_get_finisher_2022 = 'https://my1.raceresult.com/163116/RRPublish/data/list?key=c44dcccd62944fa3215da6b7de0cda77&listname=Result%20Lists%7C1.Finisher%20List%20(Ngot)&page=results&contest='

    ## prepare all participants data
    raw_data = requests.get(participants_2022).json()['data']
    for c in contest_btc:
         for raw_participant in raw_data[c]:
             strContest = c.split('_')[1]

             # fix missing data   
             if (raw_participant[0] == '5152'):
                 raw_participant[5] = 'Female under 20'

             age_group = raw_participant[5].split(' ')[1]
             
             participant = list(raw_participant) 
             # to remove duplicated BIB
             participant.pop(2)
             participant.insert(0, strContest)
             participant[5] = age_group.replace('under', '< ')
             all_participants.append(participant)
    df = pd.DataFrame(all_participants, columns=['Distance', 'BIB', 'Name', 'Gender', 'Birth', 'AG', 'Club'])
    df['Age'] = today.year - df['Birth'].astype(int)

    ## prepare finisher data
    # for ck in contest.keys():
    #     url_data = url_get_finisher_2022 + str(ck)
    #     raw_data = requests.get(url_data).json()['data'][contest[ck]]
    #     finisher[ck] = raw_data
    return df
df = prepare_data()
app.layout = dmc.Container([html.Div(col_table(df))], fluid=True)

## build api for test
@server.route('/data', methods=['GET'])
def data_contest():
    data_response = df.head(10).to_json()
    return data_response, header_response

if __name__ == '__main__':
    app.run_server(debug=True)
