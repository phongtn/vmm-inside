import dash_mantine_components as dmc
from dash import dash_table, html, Dash, dcc
import dash_ag_grid as dag
import country_converter as coco
import datetime
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

text_gradient = {"from": "red", "to": "yellow", "deg": 45}

# stylesheet for table's column
col_style = {
    "border": f"0px solid {dmc.theme.DEFAULT_COLORS['indigo'][4]}",
    "textAlign": "center",
}


def col_text(txt_value):
    return dmc.Text(txt_value,
                    variant="gradient",
                    align="center",
                    gradient=text_gradient,
                    size="xl",
                    weight=700)


# https://dash.plotly.com/datatable/interactivity
def col_table(data_frame):
    # return dash_table.DataTable(data=data_frame.to_dict('records'),
    #                             page_size=10,
    #                             sort_action="native",
    #                             sort_mode="multi",
    #                             style_table={'overflowX': 'auto'})
    return dag.AgGrid(rowData=data_frame.to_dict('records'),
                      columnDefs=[{"field": i} for i in data_frame.columns],
                      columnSize="sizeToFit",
                      defaultColDef={"resizable": True,
                                     "sortable": True, "filter": True},
                      dashGridOptions={"pagination": True, }
                      )


def transform_data(participants, year=2023, contest='#all'):
    if year == '2023':
        # print('query this year: %s' %year)
        return pd.DataFrame(participants, columns=['BIB', 'Distance', 'Name', 'Gender', 'Birth', 'Country', 'Club'])
    else:
        # print('query old year: %s and contest: %s' %( year, contest) )
        df = pd.read_csv('history/result2022.csv')
        if ('#all' == contest):             
            return df
        else:
            return df.loc[df['Distance'] == contest]


def grid_contest(participants, year, contest='#all'):
    today = datetime.date.today()
    cc = coco.CountryConverter()

    # Create a DataFrame
    # df = pd.DataFrame(participants, columns=[
    #                   'BIB', 'Distance', 'Name', 'Gender', 'Birth', 'Country', 'Club'])

    df = transform_data(participants, year, contest)

    # compute average age of participants
    df['Age'] = today.year - df['Birth'].astype(int)

    avg_age = round(df['Age'].mean(), 1)
    avg_age_gender = df[['Gender', 'Age']].groupby('Gender').mean()
    # print(avg_age)
    # print(avg_age_gender)

    # count the number of participants
    total_runner = df.shape[0]
    total_finished = 0
    total_dnf = 0
    if 'Status' in df:
        total_finished = df.loc[df['Status'] == 'Finish'].shape[0]
        total_dnf = df.loc[df['Status'] == 'DNF'].shape[0]

     # check club   
    vmm_club = df[df['Club'] != '']

    # Count by age group
    # age_group = df.iloc[:, 3:8]
    age_ranges = range(10, 100, 5)
    labels = [
        f"{start}-{start+4}" for start in age_ranges[:len(age_ranges) - 1]]
    df['AG'] = pd.cut(df['Age'], bins=age_ranges, labels=labels)
    age_group = df['AG'].value_counts().reset_index()
    age_group.columns = ['Age Group', 'Count']
    age_group_count = age_group[age_group['Count'] > 0]

    # Count the elements by country
    country_counts = df['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']

    country_counts['ISO'] = cc.pandas_convert(series=country_counts['Country'])
    country_counts['Continent'] = cc.pandas_convert(
        series=country_counts['Country'], to='Continent')

    club_counts = vmm_club['Club'].value_counts().reset_index()
    club_counts.columns = ['Club', 'Count']

    # Count the number of male and female runners
    gender_counts = df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig_gender = px.pie(gender_counts, values="Count", names="Gender", title="Gender",
                        color_discrete_sequence=px.colors.sequential.RdBu)

    fig_age_group = px.bar(age_group_count, y='Count',
                           x='Age Group', color='Count', orientation='v')

    fig_club = px.pie(club_counts.head(5), values="Count",
                      names="Club", title="Top 5 Club")

    # fig_country = px.scatter_geo(country_counts, locations="ISO",
    #                  hover_name="Country", size="Count",
    #                  color="Continent", title="By Country",
    #                  projection="natural earth")
    fig_country = px.pie(country_counts.head(
        5), values="Count", names="Country", title="Top 5 Country")

    return html.Div(
        id="specific_contest",
        children=[
            dmc.Grid(
                gutter="md",
                grow=True,
                children=[
                    dmc.Col([
                            dmc.Grid(gutter='xs', grow=True, children=[
                                dmc.Col(
                                    [col_text(f"Total: {total_runner}")], span='content'),
                                dmc.Col(
                                    [col_text(f"Finish: {total_finished}")], span='content'),
                                dmc.Col(
                                    [col_text(f"DNF: {total_dnf}")], span='content'),
                            ])], style=col_style, span=12),
                    # Second row
                    dmc.Col([
                        dmc.Grid(gutter='xs', grow=True, children=[
                            dmc.Col([dcc.Graph(figure=fig_age_group)],
                                    span='auto'),
                        ])
                    ], style=col_style, span=12),
                    dmc.Col([
                        dmc.Grid(gutter='xs', grow=True, children=[
                            dmc.Col([dcc.Graph(figure=fig_gender)],
                                    span='auto'),
                            dmc.Col([dcc.Graph(figure=fig_country)],
                                    span='auto'),
                        ])
                    ], style=col_style, span=12),
                    # Next Row
                    dmc.Col([
                        dmc.Grid(gutter=68, grow=True, children=[
                            dmc.Col([col_table(country_counts)], span=4),
                            dmc.Col([dcc.Graph(figure=fig_club)], span=5),
                            dmc.Col([col_table(club_counts)], span=3),
                        ])
                    ], style=col_style, span=12),
                    # dmc.Col([col_table(age_group_count)],
                    #         span=4),
                    dmc.Col([col_table(df)],
                            span=12),

                ]
            )])
