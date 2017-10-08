import sys
import pymongo
import pandas as pd
#from pymongo import Connection

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
from datetime import datetime
from pytz import timezone

import base64
import json
import pandas as pd
import plotly
import io
import numpy as np

from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://andrew:linxie@ds044689.mlab.com:44689/meraki")
df = pd.DataFrame(list(client.meraki.data.find()))
#print(df.to_string())
# df = df.groupby(['application'])['numClients'].sum()
df_agg = df.groupby('application')['numClients','recv','sent'].sum().reset_index()
df_agg = df_agg[df_agg.application != "Miscellaneous secure web"]
df_agg = df_agg[df_agg.application != "Miscellaneous web"]

#print(df.head)
df_agg_num = df_agg.sort_values('numClients', ascending = False)
#print(df_agg_num.head)
df_agg_rec = df_agg.sort_values('recv', ascending = False)
df_agg_sent = df_agg.sort_values('sent', ascending = False)
top_sites = df_agg_num['application'][:10]
#print(top_sites.iloc[0])
for index, row in df.iterrows():
    df.at[index, '_id'] = row['_id'].generation_time.astimezone(timezone('US/Pacific'))
time_stamps = df['_id'].unique()
datas = []
for i in range(10):
    df_site = df.loc[df['application'] == top_sites.iloc[i]]
    df_site = df_site.sort_values('_id')
    datas.append(go.Scatter(
        x = [str(time) for time in time_stamps],
        y = df_site['numClients'].tolist(),
        mode = 'lines+markers',
        name = top_sites.iloc[i]
    ))


student_lst = list(client.meraki.students.find())
check_in = client.meraki.locations
parse_date = lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')
student_info = []
students_not_found = []
for student in student_lst:
    times_seen = [parse_date(x['seenTime']) for x in list(check_in.find({'clientMac': student['clientMac']}))]
    num_ping = len(times_seen)
    if num_ping == 0:
        students_not_found.append({'Name': student['name'], 'SID': student['SID']})
    else:
        t_d = max(times_seen) - min(times_seen)
        range_sec = t_d.seconds
        student_info.append({'Name': student['name'], 'SID': student['SID'], 'Num Ping': num_ping, 'Time Range': range_sec, 'Last Seen': max(times_seen)})
student_info_table = pd.DataFrame(student_info)
del student_info_table['Last Seen']
del student_info_table['Num Ping']
student_info_table_cols = student_info_table.columns.tolist()
indexOfName = student_info_table_cols.index("Name")
student_info_table_cols.insert(0,student_info_table_cols.pop(indexOfName))
student_info_table = student_info_table[student_info_table_cols]
attendance_col = []
for index, row in student_info_table.iterrows():
    if (row['Time Range'] > 10000):
        attendance_col.append("Present")
    else:
        attendance_col.append("Partially attended")
student_info_table.insert(loc=3, column='Attendance status', value=attendance_col)
student_info_table = student_info_table[['Name', 'SID', 'Time Range', 'Attendance status']]
student_info = pd.DataFrame(student_info[:50])
students_completely_absent = pd.DataFrame(students_not_found)
students_completely_absent_cols = students_completely_absent.columns.tolist()
indexOfName = students_completely_absent_cols.index("Name")
students_completely_absent_cols.insert(0,students_completely_absent_cols.pop(indexOfName))
students_completely_absent = students_completely_absent[students_completely_absent_cols]
students_completely_absent = students_completely_absent[['Name', 'SID']]


student_graphs = []
for i in range(len(student_info[:50])):
    print ("x is " + str(student_info.at[i,'Name']))
    print("y is " + str(student_info.at[i, 'Num Ping']))
    student_graphs.append({'x': [student_info.at[i,'Name'] ], 'y': [student_info.at[i, 'Time Range']], 'type': 'bar', 'name': student_info.at[i,'Name']})





y = df[(df['_id']==time_stamps[0])]['numClients']

y = [df[(df['_id']==x) & (df['application'] == top_sites.iloc[0])]['numClients'] for x in time_stamps]


app = dash.Dash()
server = app.server
# app.scripts.config.serve_locally = True

app.layout = html.Div([
    html.H1(children = "STAY PRESENT", style = {'textAlign': 'center', "size": '75'}),
    html.Div([
        html.P("Use this application to monitor your student's device usage during class based on their communications\
            with WiFi routers installed right in your classroom/lecture hall!"),
        html.P("If it is presumed that students use their phones right before and right after a lecture, \
            the time where students check in and out of a wireless internet server in the proximity of the \
            lecture hall can be a good indicator that they are present throughout a lecture. Students that do \
            not even have their devices checked in at all could be considered absent (Or without an internet-enabled \
            device) as shown below. These are shown in the first 3 charts."),
        html.P("Although the communication of students' devices with a WiFi network can be a good indicator of physical presence, \
            we know that educators everywhere want to make sure that students are actually mentally present instead of actively engaging \
            with all the Snapchat-Insta-Facebook like activity possible on \
            their devices. Therefore we have also provided data on the sort of online websites your students interact with whilst they are in class. \
            The bottom half of the page shows metrics on what sort of websites send the most information \
            to your students (Pie Chart 2), engage most of your device-using students (Pie Chart 1), and \
            demand the most information from your students (Pie Chart 3. May or may not be correlated with student distractedness). \
            Along with those, we present a grouped bar chart of the tradeoff between information sent and received for Popular \
            websites your students interact with. Finally, we have a time series of the number of your students actually interacting \
            with certain popular websites during class time...\
            ")
        ]),
    dcc.Graph(
        id='student_attendance',
        figure={
            'data': student_graphs,
            'layout': {
                'title': 'Approximate Student Duration in Class (Student Wifi Network Entrance and Exit Intervals In Seconds). '
            }
        }
    ),
    html.H3('Present students statuses'),
    dt.DataTable(rows=student_info_table.to_dict('records')),
    html.H3('Absent students'),
    dt.DataTable(rows=students_completely_absent.to_dict('records')),
    html.Div([
        html.Div([
            dcc.Graph(
                id='numClients',
                #style={'height': 400, 'width': 400},
                figure={
                    'data': [
                        go.Pie(
                            labels=df_agg_num['application'][:10],
                            values = df_agg_num['numClients'][:10]
                        )
                    ],
                    'layout': {
                        'title': 'What Sites are your Students Visiting the Most?'
                    }
                }
            )
        ],
        style = {'display': 'inline-block', 'width': '27%'}),
        html.Div([
            dcc.Graph(
                id='dataReceived',
                #style= {width: 40%},#{'height': , 'width': 700},
                figure={
                    'data': [
                        go.Pie(
                            labels=df_agg_rec['application'][:10],
                            values = df_agg_rec['recv'][:10]
                        )
                    ],
                    'layout': {
                        'title': 'Which Sites are Sending the Most Information to your Students?'
                    }
                }
            )
        ],
        style = {'width': '30%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(
                id='dataSent',
                #style={'width': '40%'},#{'height': 400, 'width': 400},
                figure={
                    'data': [
                        go.Pie(
                            labels=df_agg_sent['application'][:10],
                            values = df_agg_sent['sent'][:10]
                        )
                    ],
                    'layout': {
                        'title': 'Which Sites are your Students Sending the Most Information to??'
                    }
                }
            )
        ],
        style = {'display': 'inline-block', 'width': '30%'}),

    ]),

    dcc.Graph(
        id='sent_vs_rec',
        figure={
            'data': [
                {'x': df_agg_num['application'][:10], 'y': df_agg_num['recv'][:10], 'type': 'bar', 'name': 'Received'},
                {'x': df_agg_num['application'][:10], 'y': df_agg_num['sent'][:10], 'type': 'bar', 'name': 'Sent'},
            ],
            'layout': {
                'title': 'The Tradeoff of Sent and Received Information (In Number of Bytes) For Popular Websites Students Visit'
            }
        }
    ),
    dcc.Graph(
        id = 'num_clients_over_time',
        style={'height': 800, 'width': '100%'},
        figure = { 'data': datas,
            'layout': {
                'title': 'Number of Students accessing Certain Websites Over Time'
            }

        }
    )

])


app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

if __name__ == '__main__':
    app.run_server(debug=True)
