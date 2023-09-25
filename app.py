import requests
import datetime
import dash_mantine_components as dmc
import country_converter as coco
from dash import Dash, callback, Output, Input
from component import grid_contest
import pandas as pd
from flask import request


external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

today = datetime.date.today()
cc = coco.CountryConverter()

# URL to fetch the JSON data from
url_all_contest = "https://my1.raceresult.com/231112/RRPublish/data/list?key=fb210544f9e10078aca7ea17ad42586f&listname=Participants%7CParticipants%20List%20123&page=participants&contest=0&r=all&l=0"
url_2022 = "https://my1.raceresult.com/163116/RRPublish/data/list?key=c44dcccd62944fa3215da6b7de0cda77&listname=Participants|Participants%20List%20123&page=participants&contest=100&r=all&l=0"

json_data = {}

# Make a GET request to the URL
response = requests.get(url_all_contest)
# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Get the JSON data from the response
    json_data = response.json()
    default_slected = '#2_Ultra 100km'

    participants = json_data['data'][default_slected]
    # Print the DataFrame
    contest_options = [["#4_10km", "10K"],
                       ["#5_21km", "21K"],
                       ["#8_Ultra 50km", "50K"],
                       ["#3_Ultra 70km", "70K"],
                       [default_slected, "100K"],
                       ["#all", "All"]]
    contest_select = [
        {"value": "#4_10km", "label": "10k"},
        {"value": "#5_21km", "label": "21k"},        
        {"value": "#8_Ultra 50km", "label": "50k"},
        {"value": default_slected, "label": "100k"},
        {"value": "#all", "label": "All"}
    ]

    year_select = [
        {"value": "2022", "label": "2022"},
        {"value": "2023", "label": "2023"},                
        {"value": "#all", "label": "All"}
    ]

    app.layout = dmc.Container([
        dmc.Title('Inside the VMM Participants', color="blue", size="h4", align='center'),

        dmc.Select(
            label="Select a contest",
            placeholder="Select one",
            id="contest-select-box",
            value=default_slected,
            data=contest_select,
            style={"width": 200, "marginBottom": 10},
        ),

        dmc.Select(
            label="Select a year",
            placeholder="Select one",
            id="year-select-box",
            value="2023",
            data=year_select,
            style={"width": 200, "marginBottom": 10},
        ),

        contest_layout := grid_contest(participants=participants, year=2023),
    ], fluid=True)
else:
    print("Error: Failed to retrieve JSON data. Status code:", response.status_code)


@callback(
    Output(contest_layout, "children"),
    Input("contest-select-box", "value"),
    Input("year-select-box", "value"))
def make_contest_grid(contest, year):
    print('select contest: ' + contest)
    if ('#all' == contest):
        all_contest = []
        for e in contest_options[:len(contest_options) - 1]:
            data_contest = json_data['data'][e[0]]
            for i in data_contest:
                all_contest.append(i)
        return grid_contest(all_contest, year)
    else:
        return grid_contest(json_data['data'][contest], year, contest)


@server.route('/data', methods=['GET'])
def data_contest():
    args = request.args
    data_size = args.to_dict().get('size')
    df = pd.DataFrame(participants, columns=[
                      'BIB', 'Distance', 'Name', 'Gender', 'Birth', 'Country', 'Club'])
    df['Age'] = today.year - df['Birth'].astype(int)
    header_response = {'Content-Type': 'application/json; charset=utf-8'}
    data_response = df.to_json()
    if data_size != None:
        data_response = df.head(int(data_size)).to_json()
    return data_response, header_response


if __name__ == '__main__':
    app.run_server(debug=True)
