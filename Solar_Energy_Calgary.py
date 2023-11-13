#!/usr/bin/env python
# coding: utf-8

# In[6]:


import dash


# In[14]:


from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


# In[61]:


#Solar Production data 
solar_df = pd.read_csv('Solar_Energy_Production_20231103.csv')
filtersolar_df = solar_df.drop(['id', 'public_url','installationDate','uid'], axis = 1)
filtersolar_df['date'] = pd.to_datetime(filtersolar_df['date'])
sum_solar= filtersolar_df.groupby(pd.Grouper(key='date',freq='M')).agg({'kWh':'sum'}).reset_index()
sum_solar['Month'] = pd.DatetimeIndex(sum_solar['date']).month_name()
sum_solar['Year'] = sum_solar['date'].dt.strftime('%Y')
sum_solar = sum_solar[(sum_solar['date'] > "2016-12-31") & (sum_solar['date'] < "2023-01-31")].reset_index()
#display(sum_solar)

# Calgary Monthly Temperatures 
weather_df = pd.read_csv('/Users/aprilng/Downloads/weatherstats_calgary_daily.csv')
weather_df['date'] = pd.to_datetime(weather_df['date'])
mean_temp= weather_df.groupby(pd.Grouper(key='date',freq='M')).agg({'avg_temperature':'mean'}).reset_index()
mean_temp['Month'] = pd.DatetimeIndex(mean_temp['date']).month_name()
mean_temp['Year'] = mean_temp['date'].dt.strftime('%Y')
mean_temp = mean_temp[(mean_temp['Year'] > "2016") & (mean_temp['Year'] < "2023")]
mean_temp.reset_index()

#Calgary Monthly Average Daylight Hours
mean_daylight= weather_df.groupby(pd.Grouper(key='date',freq='M')).agg({'daylight':'mean'}).reset_index()
mean_daylight['Month'] = pd.DatetimeIndex(mean_daylight['date']).month_name()
mean_daylight['Year'] = mean_daylight['date'].dt.strftime('%Y')
mean_daylight = mean_daylight[(mean_daylight['Year'] > "2016") & (mean_daylight['Year'] < "2023")]
mean_daylight.reset_index()
#display(mean_daylight)

#Merge 3 dataframes
merged_df = pd.merge(sum_solar, mean_temp, on='date')
merged_df = pd.merge(merged_df, mean_daylight, on='date')

# Create a dictionary to map old column names to new column names
column_name_mapping = {'Month': 'Month_z', 'Year': 'Year_z'}

# Change multiple column names using the dictionary
merged_df.rename(columns=column_name_mapping, inplace=True)
display(merged_df)


# In[73]:


# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'max-width': '1200px', 'margin': 'auto'}, children=[
    html.H1("Calgary Solar Energy Dashboard", style={'text-align': 'center', 'color': '#2a3f5f'}),
    
    # Dropdown bar chart
    html.Div([
        dcc.Markdown('**Bar Chart (Solar Production by Month)**'),
        dcc.Dropdown(
            id='bar-chart-year-dropdown',
            options=[{'label': str(year), 'value': year} for year in merged_df['Year_x'].unique()],
            value=merged_df['Year_x'].max(),
            style={'width': '50%', 'margin-bottom': '20px'}
        ),
        dcc.Graph(id='bar-chart-dropdown'),
    ]),
    
    # Heatmap for Solar Production Patterns
    html.Div([
        dcc.Markdown('**Heatmap (Solar Production Patterns)**'),
        dcc.Graph(
            id='heatmap',
            figure=px.density_heatmap(
                sum_solar,
                x='Month',
                y='Year',
                z='kWh',
                color_continuous_scale='Inferno',  # Choose a color scale
                labels={'kWh': 'Solar Production (kWh)'},
                title='Solar Production Patterns (Month vs Year)'
            ).update_layout(
                xaxis_title='Month',
                yaxis_title='Year',
                font=dict(family='Arial, sans-serif', size=12, color='#555'),
                paper_bgcolor='#f9f9f9',
                plot_bgcolor='#f9f9f9',
                margin=dict(l=40, r=40, t=40, b=40),
            ),
        ),
    ]),

    # Dropdown scatter plot for Solar Production vs Temperature
    html.Div([
        dcc.Markdown('**Scatter Plot (Solar Production vs Temperature)**'),
        dcc.Dropdown(
            id='scatter-plot-year-dropdown',
            options=[{'label': str(year), 'value': year} for year in merged_df['Year_y'].unique()],
            value=merged_df['Year_y'].max(),
            style={'width': '50%', 'margin-bottom': '20px'}
        ),
        dcc.Graph(id='scatter-plot-dropdown'),
    ]),
    
    # Dropdown scatter plot for Daylight Hours vs Solar Production
    html.Div([
        dcc.Markdown('**Scatter Plot (Daylight Hours vs Solar Production)**'),
        dcc.Dropdown(
            id='daylight-scatter-year-dropdown',
            options=[{'label': str(year), 'value': year} for year in merged_df['Year_z'].unique()],
            value=merged_df['Year_z'].max(),
            style={'width': '50%', 'margin-bottom': '20px'}
        ),
        dcc.Graph(id='daylight-scatter-plot'),
    ]),
])

# Callback to update the bar chart based on the selected year in the dropdown
@app.callback(
    Output('bar-chart-dropdown', 'figure'),
    [Input('bar-chart-year-dropdown', 'value')]
)
def update_bar_chart(selected_year):
    filtered_df = merged_df[merged_df['Year_x'] == selected_year]
    fig = px.bar(filtered_df, x='Month_x', y='kWh', color=filtered_df['kWh'], 
    color_continuous_scale=px.colors.sequential.Inferno, title=f'Monthly Solar Production ({selected_year})')
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Solar Production',
        font=dict(family='Arial, sans-serif', size=12, color='#555'),
        paper_bgcolor='#f9f9f9',  # Background color
        plot_bgcolor='#f9f9f9',   # Plot area color
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig

# Callback to update the scatter plot based on the selected year in the dropdown
@app.callback(
    Output('scatter-plot-dropdown', 'figure'),
    [Input('scatter-plot-year-dropdown', 'value')]
)
def update_scatter_plot(selected_year):
    filtered_df = merged_df[merged_df['Year_y'] == selected_year]
    fig = px.scatter(
        filtered_df, 
        x='avg_temperature', 
        y='kWh', 
        text='Month_y',
        color='Month_y', 
        title=f'Solar Production vs Temperature ({selected_year})',
        labels={'avg_temperature': 'Temperature (°C)', 'kWh': 'Solar Production (kWh)'},
        size_max=50,  # Set the maximum marker size
        size='kWh',  # Size markers based on solar production
        hover_name='Month_y',  # Show month on hover
        hover_data={'avg_temperature': True, 'kWh': ':.2f'},  # Display additional data on hover
    )
    # Customize layout
    fig.update_layout(
        xaxis_title='Temperature (°C)',
        yaxis_title='Solar Production',
        font=dict(family='Arial, sans-serif', size=12, color='#555'),
        paper_bgcolor='#f9f9f9',  # Background color
        plot_bgcolor='#f9f9f9',   # Plot area color
        margin=dict(l=40, r=40, t=40, b=40),
    )

    return fig

# Callback to update the daylight scatter plot based on the selected year in the dropdown
@app.callback(
    Output('daylight-scatter-plot', 'figure'),
    [Input('daylight-scatter-year-dropdown', 'value')]
)
def update_daylight_scatter_plot(selected_year):
    filtered_df = merged_df[merged_df['Year_z'] == selected_year]
    fig = px.scatter(
        filtered_df, 
        x='daylight', 
        y='kWh', 
        text='Month_z',
        title=f'Monthly Daylight Hours vs Solar Production ({selected_year})',
        labels={'daylight': 'Daylight Hours', 'kWh': 'Solar Production'},
        color='Month_z', 
        size_max=50,
        size='kWh',
        hover_name='Month_z',  # Show month on hover
        hover_data={'daylight': True, 'kWh': ':.2f'},  # Display additional data on hover
    )
    # Customize layout
    fig.update_layout(
        xaxis_title='Daylight Hours',
        yaxis_title='Solar Production',
        font=dict(family='Arial, sans-serif', size=12, color='#555'),
        paper_bgcolor='#f9f9f9',  # Background color
        plot_bgcolor='#f9f9f9',   # Plot area color
        margin=dict(l=40, r=40, t=40, b=40),
    )

    return fig
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




