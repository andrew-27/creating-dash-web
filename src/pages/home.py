import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import pandas as pd

dash.register_page(__name__)

layout = html.Div([
    html.H1("This is the Home Page"),
    html.Br(),
    html.Br(),
    html.H3("Please select one of the pages to continue exploring dashboard")
])