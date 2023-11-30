import pandas as pd
import numpy as np
import dash
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
dash.register_page(__name__)

def transform(str_lst):
    str_lst = str_lst.replace('[', '')
    str_lst = str_lst.replace(']', '')
    str_lst = str_lst.replace(',', '')

    return str_lst.split(" ")

def replace(str_lst):
    str_lst = str_lst.replace('[', '')
    str_lst = str_lst.replace(']', '')
    str_lst = str_lst.replace('\'', '')

    return str_lst

# -- Import and clean data
all_data = pd.read_csv("new_data.csv")
prof_names = list(all_data['Full Name'].unique())

data = pd.read_csv("full_data.csv")
data['authors'] = [replace(x) for x in data['author']]
data = data.drop(columns = {'Unnamed: 0','author'})

opt_lst = ['Citation by year','Research by type', 'Research by year', 'Research by venue']
options = [{'label': opt_lst[i], 'value': opt_lst[i]} for i in range(len(opt_lst))]

options_type = list(data['type'].unique())
options_event = list(data['event'].unique())
options_year = list(data['year'].unique())

layout = html.Div([
    html.H1("Enter Professor Name"),
    dcc.Dropdown(id = "prof_names", options = prof_names),
    html.Br(),
    html.Br(),
    html.Br(),

    html.H1(id = 'name-prof',style = {'textAlign': 'center','fontSize':32}),
    html.Div(id = "email-prof"),
    html.Div(id = "web-prof"),
    html.Div(id = "interest-prof"),

    html.Br(),

    html.Div([
        (html.Div(id = 'type_drop_txt', children = "Filter by type", style = {'width': '33%','display': 'inline-block'})),
        (html.Div(id = 'event_drop_txt', children ="Filter by event", style = {'width': '33%','display': 'inline-block'})),
        (html.Div(id = 'year_drop_txt', children = "Filter by year", style = {'width': '33%','display': 'inline-block'}))

    ],className = "row"),

    html.Div([
        html.Div([
            type_drop := dcc.Dropdown(id="filter_type", options=options_type, multi=True,style={'width': "33%",'display': 'inline-block'}),
            event_drop := dcc.Dropdown(id="filter_event", options=options_event, multi=True,style={'width': "33%",'display': 'inline-block'}),
            year_drop := dcc.Dropdown(id="filter_year", options=options_year, multi=True,style={'width': "33%",'display': 'inline-block'}),
        ]),
    ],className= "row"),

    dash_table.DataTable(id = "research_data", data = data.to_dict('records'), sort_action = "native", page_size = 10,
                         style_data={'whiteSpace': 'normal', 'height': 'auto'},style_cell={'textAlign': 'left'}
                         ),
    html.Br(),

    html.H2("Researcher Statistics"),

    html.Div([
        dcc.Dropdown(id="slct_opt",options=options,multi=False,style={'width': "40%",'display' : 'inline-block'}),
        dcc.Checklist(id = 'checklist',options=options_type,style = {'width': "33%",'display' : 'none'}),
        dcc.Dropdown(id='top_n',options = [5,10,15,20],value = 10,style = {'width': "33%",'display' : 'none'})
    ], className = "row"),

    dcc.Graph(id='gap_dash', figure={}, style = {'display' : 'none'}),

    html.Br(),

    html.H2("Researcher Network"),

    html.Div([
        dcc.Dropdown(id="network_opt", options=['Top Co-Authors','SCSE or Not'], multi=False, style={'width': "45%", 'display': 'inline-block'}),
        dcc.Dropdown(id='top_n_network', options=[5, 10, 15, 20], value=10, style={'width': "45%", 'display': 'inline-block'})
    ], className="row"),

    dcc.Graph(id='network_graph', figure={}, style = {'display' : 'none'}),

])
# ------------------------------------------------------------------------------
# App layout

# ------------------------------------------------------------------------------
@callback(
    Output(component_id='name-prof',component_property='children'),
    Output(component_id='email-prof',component_property='children'),
    Output(component_id='web-prof',component_property='children'),
    Output(component_id='interest-prof',component_property='children'),
    Output(component_id='gap_dash',component_property='style'),
    Output(component_id='network_graph',component_property='style'),
    [Input(component_id='prof_names',component_property='value')]
)

def getName(name_slctd):
    i = all_data.index[all_data['Full Name'] == name_slctd][0]
    name = "{}".format(name_slctd)
    email = "Email : " + all_data['Email'][i]
    web = "Website : " + all_data['Website URL'][i]
    interest = all_data['interest'][i]
    interest = interest.replace("[", "")
    interest = interest.replace("]", "")
    interest = interest.replace("\'", "")
    str_interest = "Research Interest : " + str(interest)

    return name, email, web, str_interest, {'display' : 'block'}, {'display' : 'block'}

@callback(
    Output(component_id='checklist', component_property='style'),
    Output(component_id='top_n', component_property='style'),
    [Input(component_id='slct_opt', component_property='value')]
)

def display(opt_slctd):
    if opt_slctd == 'Research by type':
        visible_cl = {'display': 'inline-block'}
        visible_top = {'display': 'none'}
    elif opt_slctd == 'Research by venue':
        visible_cl = {'display': 'none'}
        visible_top = {'display': 'inline-block'}
    elif opt_slctd == 'Research by year':
        visible_cl = {'display': 'none'}
        visible_top = {'display': 'none'}
    elif opt_slctd == 'Research by co-author':
        visible_cl = {'display': 'none'}
        visible_top = {'display': 'inline-block'}
    else:
        visible_cl = {'display': 'none'}
        visible_top = {'display': 'none'}

    return visible_cl, visible_top

@callback(
     Output(component_id='gap_dash', component_property='figure'),
    [Input(component_id='prof_names',component_property='value'),
        Input(component_id='slct_opt', component_property='value'),
     Input(component_id='checklist', component_property='value'),
     Input(component_id='top_n', component_property='value')]
)

def update_graph(name_slctd,opt_slctd,cl,topn):
    df = data[data['names']==name_slctd]
    if opt_slctd == 'Research by type':
        data1 = df[df['type'].isin(cl)]
        slctd_data = data1.groupby('type',as_index=False).count()[['type','name']]
        fig = px.pie(slctd_data, names='type',values='name',title="Number of {}".format(opt_slctd))
    elif opt_slctd == 'Research by venue':
        slctd_data = df.groupby('event',as_index=False).count()[['event','name']].sort_values('name',ascending = False)[:topn]
        fig = px.pie(slctd_data, names='event',values='name',title="Number of {}".format(opt_slctd))
    elif opt_slctd == 'Research by year':
        df['year'] = df['year'].astype(str)
        data1 = df.sort_values('year')
        slctd_data = data1.groupby('year', as_index=False).count()[['year', 'name']]
        fig = px.histogram(slctd_data, x='year', y='name', title="Number of {}".format(opt_slctd))
    else:
        opt_slctd = "Citations by year"
        i = all_data.index[all_data['Full Name'] == name_slctd][0]
        yr = all_data['year'][i]
        new_yr = transform(yr)
        hist = all_data['hist_data'][i]
        new_hist = [int(x) for x in transform(hist)]

        new_dict = {'year': new_yr, 'data': new_hist}
        slctd_data = pd.DataFrame(new_dict)
        fig = px.histogram(slctd_data, x='year', y='data',title="Number of {}".format(opt_slctd))

    return fig

@callback(
     Output(component_id='network_graph', component_property='figure'),
    [Input(component_id='prof_names',component_property='value'),
        Input(component_id='network_opt', component_property='value'),
     Input(component_id='top_n_network', component_property='value')]
)

def update_graph(name_slctd,opt_slctd,topn):
    i = all_data.index[all_data['Full Name'] == name_slctd][0]
    auth = all_data['counter_auth'][i]
    new_auth = replace(auth).split(",")
    if opt_slctd == 'SCSE or Not':
        cnt = 0
        for aut in new_auth:
            if aut in prof_names:
                cnt+=1
        new_dict = {'idx': ['SCSE','Not SCSE'], 'val' : [cnt, len(prof_names)-cnt]}
        slctd_data = pd.DataFrame(new_dict)
        fig = px.pie(slctd_data, names='idx', values='val', title="Number of {}".format(opt_slctd))
    else:
        tot = all_data['counter_tot'][i]
        new_tot = [int(x) for x in transform(tot)]

        new_dict = {'auth': new_auth, 'data': new_tot}
        slctd_data = pd.DataFrame(new_dict)
        slctd_data = slctd_data.sort_values('data')[-topn:]
        fig = px.pie(slctd_data, names='auth',values='data',title="Number of {}".format(opt_slctd))

    return fig

@callback(
    Output(component_id='research_data', component_property='data'),
    Output(type_drop,component_property='options'),
    Output(event_drop,component_property='options'),
    Output(year_drop,component_property='options'),
    [Input(component_id='prof_names',component_property='value'),
     Input(type_drop, 'value'),
    Input(event_drop, 'value'),
     Input(year_drop,'value')]
)

def update_table(prof_name,types, events, years):
    df = data[data['names']==prof_name]

    df['types'] = np.where(df['type'] == 'j', 'Journal',
                           np.where(df['type'] == 'c', 'Conference',
                                    np.where(df['type'] == 'i', 'Informal',
                                             np.where(df['type'] == 'r', 'Reference',
                                                      np.where(df['type'] == 'p', 'Books', 'Editor')))))
    df = df.drop(columns={'names', 'type'})

    options_type = list(df['types'].unique())
    options_event = list(df['event'].unique())
    options_year = list(df['year'].unique())

    if types:
        df = df[df['types'].isin(types)]
    if events:
        df = df[df['event'].isin(events)]
    if years:
        df = df[df['year'].isin(years)]


    return df.to_dict('records'), options_type, options_event, options_year

if __name__ == '__main__':
    app.run_server(debug=True, port = 8051)