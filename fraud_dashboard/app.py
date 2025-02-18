# app.py
from flask import Flask, jsonify
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import requests
import ipaddress

# Initialize Flask app
app = Flask(__name__)

# ====================================================================
# Flask Backend (Data API Endpoints)
# ====================================================================

# Load and preprocess data
fraud_data = pd.read_csv('../data/cleaned_fraud_data.csv')
ip_country = pd.read_csv('../data/IpAddress_to_Country.csv')

# Merge with geolocation data
def convert_ip(ip):
    try:
        return int(ipaddress.IPv4Address(ip))
    except ipaddress.AddressValueError:
        return None

fraud_data['ip_int'] = fraud_data['ip_address'].apply(convert_ip)
fraud_data = fraud_data.dropna(subset=['ip_int'])

for _, row in ip_country.iterrows():
    mask = (fraud_data['ip_int'] >= row['lower_bound_ip_address']) & (fraud_data['ip_int'] <= row['upper_bound_ip_address'])
    fraud_data.loc[mask, 'country'] = row['country']

# Convert timestamps to datetime
fraud_data['purchase_time'] = pd.to_datetime(fraud_data['purchase_time'])

@app.route('/api/stats')
def get_summary_stats():
    total = len(fraud_data)
    fraud = fraud_data['class'].sum()
    percentage = (fraud / total) * 100
    return jsonify({
        'total_transactions': total,
        'fraud_cases': fraud,
        'fraud_percentage': round(percentage, 2)
    })

@app.route('/api/trends')
def get_fraud_trends():
    trends = fraud_data.set_index('purchase_time').resample('D')['class'].sum().reset_index()
    trends['date'] = trends['purchase_time'].dt.strftime('%Y-%m-%d')
    return jsonify(trends[['date', 'class']].to_dict('records'))

@app.route('/api/geography')
def get_geography():
    geo = fraud_data[fraud_data['class'] == 1].groupby('country').size().reset_index(name='counts')
    return jsonify(geo.to_dict('records'))

@app.route('/api/devices')
def get_device_stats():
    devices = fraud_data[fraud_data['class'] == 1].groupby('device_id').size().reset_index(name='counts')
    return jsonify(devices.sort_values('counts', ascending=False).head(10).to_dict('records'))

@app.route('/api/browsers')
def get_browser_stats():
    browsers = fraud_data[fraud_data['class'] == 1].groupby('browser').size().reset_index(name='counts')
    return jsonify(browsers.to_dict('records'))

# ====================================================================
# Dash Frontend (Dashboard)
# ====================================================================
dash_app = dash.Dash(server=app, url_base_pathname='/dashboard/')

dash_app.layout = html.Div([
    html.H1("Fraud Detection Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Summary Stats
    html.Div([
        html.Div(id='total-transactions', className='summary-box'),
        html.Div(id='fraud-cases', className='summary-box'),
        html.Div(id='fraud-percentage', className='summary-box'),
    ], className='row', style={'margin': '20px 0'}),
    
    # Time Trends
    dcc.Graph(id='fraud-trends', style={'height': '400px'}),
    
    # Geography and Devices/Browsers
    html.Div([
        dcc.Graph(id='fraud-geography', style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='fraud-devices', style={'width': '49%', 'display': 'inline-block'}),
    ]),
    
    html.Div([
        dcc.Graph(id='fraud-browsers', style={'width': '100%'})
    ]),
    
    # Refresh interval
    dcc.Interval(id='interval', interval=60*1000)  # Update every 60 seconds
])

# Callbacks
@dash_app.callback(
    [Output('total-transactions', 'children'),
     Output('fraud-cases', 'children'),
     Output('fraud-percentage', 'children')],
    [Input('interval', 'n_intervals')]
)
def update_summary(n):
    response = requests.get('http://localhost:5000/api/stats')
    data = response.json()
    return [
        html.Div([
            html.H3("Total Transactions"),
            html.P(f"{data['total_transactions']}", style={'fontSize': 24})
        ]),
        html.Div([
            html.H3("Fraud Cases"),
            html.P(f"{data['fraud_cases']}", style={'fontSize': 24, 'color': 'red'})
        ]),
        html.Div([
            html.H3("Fraud Percentage"),
            html.P(f"{data['fraud_percentage']}%", style={'fontSize': 24})
        ])
    ]

@dash_app.callback(
    Output('fraud-trends', 'figure'),
    [Input('interval', 'n_intervals')]
)
def update_trends(n):
    response = requests.get('http://localhost:5000/api/trends')
    data = pd.DataFrame(response.json())
    return px.line(data, x='date', y='class', 
                 title='Fraud Cases Over Time',
                 labels={'class': 'Fraud Cases', 'date': 'Date'})

@dash_app.callback(
    Output('fraud-geography', 'figure'),
    [Input('interval', 'n_intervals')]
)
def update_geography(n):
    response = requests.get('http://localhost:5000/api/geography')
    data = pd.DataFrame(response.json())
    return px.choropleth(data, locations='country', 
                       locationmode='country names', color='counts',
                       title='Fraud Cases by Country',
                       color_continuous_scale='Viridis')

@dash_app.callback(
    Output('fraud-devices', 'figure'),
    [Input('interval', 'n_intervals')]
)
def update_devices(n):
    response = requests.get('http://localhost:5000/api/devices')
    data = pd.DataFrame(response.json())
    return px.bar(data, x='device_id', y='counts', 
                title='Top Fraudulent Devices',
                labels={'counts': 'Fraud Cases', 'device_id': 'Device ID'})

@dash_app.callback(
    Output('fraud-browsers', 'figure'),
    [Input('interval', 'n_intervals')]
)
def update_browsers(n):
    response = requests.get('http://localhost:5000/api/browsers')
    data = pd.DataFrame(response.json())
    return px.bar(data, x='browser', y='counts', 
                title='Fraud Cases by Browser',
                labels={'counts': 'Fraud Cases', 'browser': 'Browser'})

# ====================================================================
# Run the Application
# ====================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)