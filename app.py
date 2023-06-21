import requests
import datetime
import dash_mantine_components as dmc
import country_converter as coco
from dash import Dash, callback, Output, Input
from component import col_text, col_table, grid_contest


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

    # Extract relevant data: #1_10km, #2_21km, #3_42km, #4_Ultra 100km, #5_Ultra 70km
    participants = json_data['data']['#5_Ultra 70km']

    # Print the DataFrame
    contest_options = [["#1_10km", "10K"],
                       ["#2_21km", "21K"],
                       ["#3_42km", "42K"],
                       ["#5_Ultra 70km", "70K"],
                       ["#4_Ultra 100km", "100K"],
                       ["#all", "All"]]

    app.layout = dmc.Container([
        dmc.Title('Inside the VMM Participants', color="blue", size="h4"),

        dmc.RadioGroup(
            [dmc.Radio(l, value=k) for k, l in contest_options],
            value='#4_Ultra 100km',
            size='sm',
            label='Select a contest',
            id='radio-button-contenst'),
        dmc.Text(id="radio-output"),

        contest_layout := grid_contest(participants=participants),
    ], fluid=True)
else:
    print("Error: Failed to retrieve JSON data. Status code:", response.status_code)


@callback(
    Output(contest_layout, "children"),
    Input("radio-button-contenst", "value"))
def make_contest_grid(value):
    if ('#all' == value):
        all_contest = []
        for e in contest_options[:len(contest_options) - 1]:
            data_contest = json_data['data'][e[0]]
            for i in data_contest:
                all_contest.append(i)                 
        return grid_contest(all_contest)    
    else:
        return grid_contest(json_data['data'][value])

if __name__ == '__main__':
    app.run_server(debug=True)
