import dash
from dash import dcc, html, dash_table, Input, Output, callback
import pandas as pd
import plotly.express as px


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

dash.register_page(__name__)
all_data = pd.read_csv("new_data.csv")
prof_names = list(all_data['Full Name'].unique())

opt_lst = ['Citation by year','Research by type', 'Research by year']
options = [{'label': opt_lst[i], 'value': opt_lst[i]} for i in range(len(opt_lst))]

data = pd.read_csv("full_data.csv")
data['authors'] = [replace(x) for x in data['author']]
data = data.drop(columns = {'Unnamed: 0','author'})

df = pd.read_csv("scse_data.csv")
df = df.drop(columns= {'Unnamed: 0'})

grp = pd.read_csv("group.csv")
grp['Prof Lists'] = [replace(x) for x in grp['Prof List']]
grp = grp.drop(columns= {'Unnamed: 0','Prof List'})

conf = pd.read_csv("conference_data.csv")
conf = conf.drop(columns= {'Unnamed: 0'})
options_rank = list(conf['rank'].unique())
options_rank.sort()

layout = html.Div(
    [
        html.H2("Group Researcher"),
        dcc.Dropdown(id='grp_rsc',options= ['By Expertize', 'By Research Group']),
        dash_table.DataTable(id = "grp_data",  page_size = 10,
                         style_data={'whiteSpace': 'normal', 'height': 'auto'},style_cell={'textAlign': 'left'}),

        html.H2("Compare Researcher"),
        html.Div([
            dcc.Dropdown(id = "prof1", options = prof_names, multi= False, style = {'width': '45%','display': 'inline-block'}),
            dcc.Dropdown(id = "prof2", options = prof_names, multi = False, style = {'width': '45%','display': 'inline-block'})
        ],className= "row"),

        dash_table.DataTable(id = "cmp_data",  page_size = 10,
                         style_data={'whiteSpace': 'normal', 'height': 'auto',  'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',},style_cell={'textAlign': 'left'}),
        html.Br(),
        html.Div("Researcher statistics"),
        dcc.Dropdown(id = "opt", options = options, multi = False, style= {'width' : '40%'}),
        dcc.Graph(id='graph', figure={}),

        html.Br(),
        html.H2("SCSE Weakness and Strength"),

        html.Div([
            (html.Div( children = "Select parameter", style = {'width': '50%','display': 'inline-block'})),
            (html.Div(children ="Filter Year/FoR", style = {'width': '25%','display': 'inline-block'})),
            (html.Div(children = "Filter Rank", style = {'width': '25%','display': 'inline-block'}))
        ],className = "row"),

        html.Div([
            html.Div([
            type_drop := dcc.Dropdown(id="graph_type", options=['Research by FoR','Research by Year'], multi=False,style={'width': "50%",'display': 'inline-block'}),
            event_drop := dcc.Dropdown(id="year_for", multi=True,style={'width': "25%",'display': 'inline-block'}),
            year_drop := dcc.Dropdown(id="rank",options=options_rank, multi=True,style={'width': "25%",'display': 'inline-block'}),
        ]),
    ],className= "row"),

        dcc.Graph(id = 'for_graph',figure={})

    ]
)

@callback(
    Output(component_id='grp_data',component_property='data'),
    [Input(component_id='grp_rsc',component_property='value')]
)

def extractTable(grp_by):
    if grp_by == 'By Expertize':
        dff = grp[grp['Aspect']=='Expertize']
        dff = dff.drop(columns = {'Aspect'})
        dff = dff.sort_values('Total Prof',ascending = False)
    else:
        dff = grp[grp['Aspect'] == 'Research Group']
        dff = dff.drop(columns={'Aspect'})
        dff = dff.sort_values('Total Prof',ascending = False)

    return dff.to_dict('records')

@callback(
    Output(component_id='cmp_data', component_property='data'),
    [Input(component_id='prof1',component_property='value'),
     Input(component_id='prof2',component_property='value')]
)

def getTable(prof1,prof2):
    dff = df[(df['Full Name']==prof1)|(df['Full Name']==prof2)]
    return dff.set_index('Full Name').T.rename_axis('Aspect').reset_index().to_dict('records')

@callback(
    Output(component_id='year_for',component_property='options'),
    [Input(component_id='graph_type',component_property='value')]
)

def getOptions(graph_type):
    if graph_type == 'Research by FoR':
        opt = conf['year'].unique()
    else:
        opt = conf['primaryFoR'].unique()
    opt.sort()

    return opt

@callback(
    Output(component_id='graph', component_property='figure'),
    [ Input(component_id='opt', component_property='value'),
    Input(component_id='prof1',component_property='value'),
     Input(component_id='prof2',component_property='value')]
)

def update_graph(opt_slctd,prof1,prof2):
    dff = data[(data['names']==prof1)|(data['names']==prof2)]
    if opt_slctd == 'Research by type':
        slctd_data = dff.groupby(['names','type'],as_index=False).count()
        fig = px.bar(slctd_data, x ="type", y="name", color = "names",barmode = "group",title="Number of {}".format(opt_slctd))
    elif opt_slctd == 'Research by year':
        dff['year'] = dff['year'].astype(str)
        data1 = dff.sort_values('year')
        slctd_data =  data1.groupby(['names','year'],as_index=False).count()
        fig = px.bar(slctd_data, x ="year", y="name", color = "names",barmode = "group", title="Number of {}".format(opt_slctd))
    else:
        opt_slctd = "Citations by year"

        i1 = all_data.index[all_data['Full Name'] == prof1][0]
        yr = all_data['year'][i1]
        new_yr = transform(yr)
        hist = all_data['hist_data'][i1]
        new_hist = [int(x) for x in transform(hist)]
        p_name = [prof1 for i in range(len(new_yr))]

        i2 = all_data.index[all_data['Full Name'] == prof2][0]
        yr2 = all_data['year'][i2]
        new_yr2 = transform(yr2)
        hist2 = all_data['hist_data'][i2]
        new_hist2 = [int(x) for x in transform(hist2)]
        p_name2 = [prof2 for i in range(len(new_yr2))]

        new_yr.extend(new_yr2)
        new_hist.extend(new_hist2)
        p_name.extend(p_name2)

        print(len(new_yr),len(new_hist),len(p_name))
        new_dict = {'year': new_yr, 'data': new_hist, 'prof' : p_name}
        slctd_data = pd.DataFrame(new_dict)
        fig = px.bar(slctd_data, x='year', y='data',color = "prof", barmode = "group",title="Number of {}".format(opt_slctd))

    return fig

@callback(
    Output(component_id='for_graph', component_property='figure'),
    [ Input(component_id='graph_type', component_property='value'),
    Input(component_id='year_for',component_property='value'),
     Input(component_id='rank',component_property='value')]
)

def update_graph2(type,year_for,rank):
    print(year_for)
    if rank:
        dff = conf[conf['rank'].isin(rank)]
    else:
        dff = conf.copy()
    if type == 'Research by Year':
        if year_for:
            dff1 = dff[dff['primaryFoR'].isin(year_for)]
        else:
            dff1 = dff.copy()
        grp_cnt = dff1.groupby(['year'],as_index=False).count()
        fig = px.histogram(grp_cnt,x='year',y='name')
    else:
        if year_for:
            dff1 = dff[dff['year'].isin(year_for)]
        else:
            dff1 = dff.copy()
        grp_cnt = dff1.groupby(['primaryFoR'], as_index=False).count()
        fig = px.pie(grp_cnt, names='primaryFoR', values='name')

    return fig