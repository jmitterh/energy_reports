import glob
import pandas as pd
import os
from iapws import IAPWS97
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import logging


# Configure logging
logger = logging.getLogger()  # Get the root logger
logger.setLevel(logging.INFO)

# File Handler - logs to a file
file_handler = logging.FileHandler('main.log')
file_format = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Stream Handler - logs to the console
stream_handler = logging.StreamHandler()
stream_format = logging.Formatter('%(levelname)s: %(message)s')
stream_handler.setFormatter(stream_format)
logger.addHandler(stream_handler)

def equipment_constraints(df: pd.DataFrame)-> pd.DataFrame:
    '''
    This function filters the rows based on conditions:
    The equipment is online if the Power (MW) is greater than 30 MW.
    The equipment is operating in steady state when PowerSwing (MW) is at most 3 MW.
    return:
        DataFrame: the input dataframe filtered based on the conditions
    '''

    logger.info('Filtering rows based on conditions: Power (MW) > 30 and PowerSwing (MW) <= 3')
    df_filtered = df.loc[
        (df['Power (MW)'] > 30) & 
        (df['PowerSwing (MW)'] <= 3) & 
        (df['Temp (°F)'] > 1000)
        ]
    return df_filtered


def calculate_enthalpy(row : float)-> float or None:
    '''
    This function calculates the enthalpy using the IAPWS97 standard.
    This helper function is used in the calculate_enthalpy_dataframe function.
    return:
        float: enthalpy in KJ/Kg
        None: if the calculation fails due to not meeting the IAPWS97 standard
    '''
    try:
        return IAPWS97(P=row['Press (MPa)'], T=row['Temp (K)']).h
    except NotImplementedError as e: 
        logger.warning(f"Warning for Timestamp {row['Timestamp']} P={row['Press (MPa)']}, T={row['Temp (K)']}: {e}")
        return None


def calculate_enthalpy_dataframe(df: pd.DataFrame)-> pd.DataFrame:
    '''
    This function calculates the enthalpy using the IAPWS97 standard
    return:
        DataFrame: the input dataframe with an additional column for enthalpy
    '''
    # calculate the supporting columns for Enthalpy (BTU/lb)
    df['Press (psia)'] = df['Press (psig)'] + 14.7
    logger.debug(f'Press (psia): \n{df["Press (psia)"]}')
    # Convert the temperature from Farenheit to Kelvin
    df['Temp (K)'] = (df['Temp (°F)'] - 32) * 5/9 + 273.15
    logger.debug(f'Temp (K): \n{df["Temp (K)"]}')
    # Convert PSIA to megapascals (MPa)
    df['Press (MPa)'] = df['Press (psia)'] * 6894.76 / 10**6 # 1,000,000 (1 psi = 6894.76 Pa)
    logger.debug(f'Press (MPa): \n{df["Press (MPa)"]}')
    # Calculate the enthalpy [KJ/Kg] using the IAPWS97 standard
    df['Enthalpy (kJ/kg)'] = df.apply(calculate_enthalpy, axis=1)
    logger.debug(f'Enthalpy (kJ/kg): \n{df["Enthalpy (kJ/kg)"]}')
    # Specific Enthalpy (BTU/lb) of Superheated Enthalpy (kJ/kg) from (kJ/kg) to (BTU/lb) conversion
    df['Enthalpy (BTU/lb)'] = df['Enthalpy (kJ/kg)'] * 0.4299226
    logger.debug(f'Enthalpy (BTU/lb): \n{df["Enthalpy (BTU/lb)"]}')

    return df


def chart_1_get_color_for_hours(hours: int, df: pd.DataFrame)-> list[str]:
    '''
    This function calculates the color scale for the hours within function chart_1
    return:
        list: color scale for the hours
    '''
    max_hours = df['Hours'].max()
    min_hours = df['Hours'].min()
    logger.debug(f'Max hours: {max_hours}, Min hours: {min_hours}')
    color_scale = np.interp(hours, [min_hours, max_hours], [0, 1]) # percentage
    color_list = []
    for c in color_scale:
        color_list.append(f'rgba(255,{int(255*(1-c))},1,0.6)')
        logger.debug(f'Color: rgba(255,{int(255*(1-c))},1,0.6)')
    return color_list


def chart_1(df: pd.DataFrame)-> str:
    '''
    This function creates a line chart of the Power (MW) and Enthalpy (BTU/lb) over time.
    Plotly px 
    return:
        HTML filename: the filename of the HTML file saved in the charts folder
    '''
    # aggregate data to quarterly and yearly
    logger.info('Aggregating data to quarterly and yearly')
    df['Quarter'] = pd.to_datetime(df['Timestamp']).dt.to_period('Q')
    df['Year'] = pd.to_datetime(df['Timestamp']).dt.year
    logger.info(f'Aggregated data to quarterly and yearly: \n{df.head()}')
    # Define temperature bins above 1000°F at increments of 50°F
    # range(start, stop, step)
    logger.info('Defining temperature bins above 1000°F at increments of 50°F')
    temp_bins = range(1000, int(df['Temp (°F)'].max()) + 50, 50)
    # Create bin labels for these bins
    bin_labels = [f'{i} - {i + 50}°F' for i in temp_bins[:-1]]
    logger.info(f'Temperature bins: {temp_bins}')
    logger.info(f'Bin labels: {bin_labels}')

    # Categorize temperature into bins
    logger.info('Categorizing temperature into bins')
    df['Temp_Range'] = pd.cut(df['Temp (°F)'], bins=temp_bins, labels=bin_labels) # , right=False (interval index ignored)
    logger.info(f'Categorized temperature into bins: \n{df.head()}')
    # Filter rows based on conditions
    # The equipment is online if the Power (MW) is greater than 30 MW.
    # The equipment is operating in steady state when PowerSwing (MW) is at most 3 MW.
    df_filtered = equipment_constraints(df)
    logger.info(f'Filtered rows based on conditions: \n{df_filtered.head()}')

    # Aggregate data: count hours within each Temp_Range for every Year-Quarter
    logger.info('Aggregating data: count hours within each Temp_Range for every Year-Quarter')
    df_agg = df_filtered.groupby(['Year', 'Quarter', 'Temp_Range'], observed=False).size().reset_index(name='Hours')

    # Convert 'Year' and 'Quarter' columns to string if they are of type Period
    df_agg['Year'] = df_agg['Year'].astype(str)
    df_agg['Quarter'] = df_agg['Quarter'].astype(str)

    # Filter out ranges with 5 hours or less
    logger.info('Filtering out ranges with 5 hours or less')
    df_agg = df_agg.loc[df_agg['Hours'] > 5]

    # Sort
    df_agg = df_agg.sort_values(['Year', 'Quarter', 'Temp_Range'])
    logger.info(f'Aggregated data: \n{df_agg.head()}')

    # threshold colors function
    logger.info('Getting color scale for the hours')
    logger.info(f"max hours:\n{df_agg['Hours'].max()}")
    hours_colors = chart_1_get_color_for_hours(df_agg['Hours'], df_agg)
    logger.info(f'Color scale for the hours: {hours_colors}')

    # Create a table
    logger.info('Creating a table')
    fig_table = go.Figure(data=[go.Table(
        header=dict(values=['Temperature Range', 'Hours', 'Quarter', 'Year']),
        cells=dict(values=[df_agg.Temp_Range, df_agg.Hours, df_agg.Quarter, df_agg.Year],
                fill=dict(color=['#F5F5F5', hours_colors, '#F5F5F5', '#F5F5F5']),
                align='center'),
        columnwidth=[100, 100, 100, 100]
    )

    ])
    # Update the layout of the table and output on browser
    filename = 'Operational Hours in Temperature Ranges Per Quarter and Year'
    fig_table.update_layout(title=filename, title_x=0.5, title_y=0.92, title_font_size=20, title_font_family='Arial')
    logger.info('Plotly shall open browser and display table (chart 1.)...')
    fig_table.write_html(f"./charts/1_{filename.replace(' ','_')}.html", auto_open=True)

    return f"1_{filename.replace(' ','_')}.html"


def chart_2_dataframe_prep(df: pd.DataFrame)-> pd.DataFrame:
    '''
    This function prepares the dataframe for the multiple different versions of chart 2 (three versions).
    return:
        DataFrame: the input dataframe ready for visualization
    '''
    # Define temperature bins above 1000°F at increments of 50°F
    logger.info('Defining temperature bins above 1000°F at increments of 10°F')
    # range(start, stop, step)
    temp_bins = range(1000, int(df['Temp (°F)'].max()) + 10, 10)
    # Create bin labels for these bins
    bin_labels = [f'{i} - {i + 10}°F' for i in temp_bins[:-1]]
    logger.info(f'Temperature bins: {temp_bins}, Bin labels: {bin_labels}')
    # Adding a label to the temperature range
    logger.info('Adding a label to the temperature range')
    df['Temp_Range'] = pd.cut(df['Temp (°F)'], bins=temp_bins, labels=bin_labels)

    df_filtered = equipment_constraints(df)
    logger.info(f'Filtered rows based on conditions: \n{df_filtered.head()}')

    # Generate a color for each temperature range
    logger.info('Generating a color for each temperature range')
    colors = px.colors.qualitative.Set1
    color_map = {label: colors[i % len(colors)] for i, label in enumerate(bin_labels)}
    # Apply the color mapping
    df_filtered['Color'] = df_filtered['Temp_Range'].map(color_map)
    logger.info(f'Color mapping: \n{df_filtered.head()}')

    return df_filtered, color_map


def chart_2_3d(df: pd.DataFrame)-> str:
    '''
    This function creates a 3D scatter plot of Enthalpy (BTU/lb) over time by temperature range.
    Plotly px
    return:
        HTML filename: the filename of the HTML file saved in the charts folder
    '''
    # Prepare the dataframe for the chart
    logger.info('Preparing the dataframe for the chart')
    df_filtered, color_map = chart_2_dataframe_prep(df)
    logger.info(f'Prepared the dataframe for the chart: \n{df_filtered.head()}')
    # Create the Plotly figure
    fig = go.Figure()
    logger.info('Creating the Plotly figure for 3D scatter plot of Enthalpy (BTU/lb) over time by temperature range')
    # Add a Scatter3d trace for each temperature range
    for temp_range, group_data in df_filtered.groupby('Temp_Range', observed=False):
        fig.add_trace(go.Scatter3d(
            x=group_data['Timestamp'], 
            y=group_data['Enthalpy (BTU/lb)'], 
            z=group_data['Temp (°F)'],
            mode='markers',
            marker=dict(
                size=3,
                color=color_map[temp_range],  # Use the color mapped for the temperature range
            ),
            name=temp_range  # Label for the legend
        ))

    filename = 'Enthalpy Over Time by Temperature Range'
    # Update layout with axis labels
    fig.update_layout(
        scene=dict(
            xaxis_title='Time',
            yaxis_title='Enthalpy (BTU/lb)',
            zaxis_title='Temperature (°F)',
        ),
        title=filename
    )
    logger.info('Plotly shall open browser and display graph (chart 2. 3d)...')
    fig.write_html(f"./charts/2.1_3D_{filename.replace(' ','_')}.html", auto_open=True)

    return f"2.1_3D_{filename.replace(' ','_')}.html"


def chart_2_2d(df: pd.DataFrame)-> str:
    '''
    This function creates a 2D scatter plot of Enthalpy (BTU/lb) over time by temperature range.
    Plotly go
    return:
        HTML filename: the filename of the HTML file saved in the charts folder
    '''
    # Prepare the dataframe for the chart
    logger.info('Preparing the dataframe for the chart')
    df_filtered, color_map = chart_2_dataframe_prep(df)
    logger.info(f'Prepared the dataframe for the chart: \n{df_filtered.head()}')
    # Create the Plotly figure for a 2D scatter plot
    fig = go.Figure()

    # Add a Scatter trace for each temperature range
    logger.info('Creating the Plotly figure for 2D scatter plot of Enthalpy (BTU/lb) over time by temperature range')
    for temp_range, group_data in df_filtered.groupby('Temp_Range', observed=False):
        fig.add_trace(go.Scatter(
            x=group_data['Timestamp'], 
            y=group_data['Enthalpy (BTU/lb)'], 
            mode='markers',
            marker=dict(
                color=group_data['Color'],
            ),
            name=temp_range 
        ))

    filename = 'Enthalpy Over Time by Temperature Range'
    # Update layout with axis labels and title
    fig.update_layout(
        xaxis_title='Timestamp',
        yaxis_title='Enthalpy (BTU/lb)',
        title=filename,
        legend_title="Temperature Range"
    )
    # Show the figure
    logger.info('Plotly shall open browser and display graph (chart 2. 2d)...')
    fig.write_html(f"./charts/2.2_{filename.replace(' ','_')}.html", auto_open=True)
    
    return f"2.2_{filename.replace(' ','_')}.html"


def chart_2_alternate(df: pd.DataFrame)-> str:
    '''
    This function creates a 2D scatter dual-axis plot of Average
    Enthalpy (BTU/lb) and Temperature over Average 24 hour period for 2 years (2015, 2016).
    Plotly go
    return:
        HTML filename: the filename of the HTML file saved in the charts folder
    '''
    # Prepare the dataframe for the chart
    logger.info('Preparing the dataframe for the chart')
    df_filtered, _ = chart_2_dataframe_prep(df)
    logger.info(f'Prepared the dataframe for the chart: \n{df_filtered.head()}')
    # Calculate the hour of the day
    df_filtered['Hour'] = df_filtered['Timestamp'].dt.hour
    # Calculate the average Enthalpy (BTU/lb) and Temperature by hour
    hourly_avg = df_filtered.groupby('Hour')[['Enthalpy (BTU/lb)', 'Temp (°F)']].mean().reset_index()
    logger.info(f'Calculated the average Enthalpy (BTU/lb) and Temperature by hour: {hourly_avg.head()}')
    # Create the Plotly figure for a 2D scatter plot
    fig = go.Figure()

    # Add a Scatter trace for average Enthalpy (BTU/lb) by hour
    fig.add_trace(go.Scatter(
        x=hourly_avg['Hour'],  
        y=hourly_avg['Enthalpy (BTU/lb)'], # First y-axis
        mode='markers+lines',  # Combine markers and lines for the plot
        name='Average Enthalpy',  # Name for the legend
        marker=dict(size=5),  # Marker size
    ))

    # Add a Scatter trace for
    fig.add_trace(go.Scatter(
        x=hourly_avg['Hour'],  
        y=hourly_avg['Temp (°F)'],  
        mode='markers+lines',  # Combine markers and lines for the plot
        name='Average Temperature',  # Name for the legend
        marker=dict(size=5),  # Marker size
        yaxis='y2'  # Assign to secondary y-axis
    ))

    filename = 'Daily Cycle Representation of Enthalpy and Temperature'
    # Update layout with axis labels and title, and create a secondary y-axis for temperature
    fig.update_layout(
        xaxis_title='Hour of Day',
        yaxis_title='Average Enthalpy (BTU/lb)',
        yaxis2=dict(
            title='Average Temperature (°F)',
            overlaying='y',
            side='right'
        ),
        title=filename+f' ({df_filtered["Timestamp"].dt.year.min()} - {df_filtered["Timestamp"].dt.year.max()})',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1), 
    )
    # Save the figure as HTML
    logger.info('Plotly shall open browser and display graph (chart 2. alternate)...')
    fig.write_html(f"./charts/2.3_{filename.replace(' ','_')}.html", auto_open=True)

    return f"2.3_{filename.replace(' ','_')}.html"





if __name__ == '__main__':
    # use glob to get all the csv files in the folder
    logger.info('\n\nLoading CSV files...')
    csv_files = glob.glob('./data/*.csv')
    # Create an empty dataframe to store the combined data
    df = pd.DataFrame()

    # Loop through each CSV file and append its contents to the combined dataframe
    for csv_file in csv_files:
        temp_df = pd.read_csv(csv_file, encoding='ISO-8859-1')
        logger.debug(f'Loaded {csv_file} with {temp_df.shape[0]} rows and {temp_df.shape[1]} columns')
        df = pd.concat([df, temp_df])
    logger.info(f'Combined dataframe has {df.shape[0]} rows and {df.shape[1]} columns')

    # aggregate 30 min interval data to hourly data
    logger.info('Aggregating 30 min interval data to hourly data...')
    df['Timestamp'] = pd.to_datetime(df['Timestamp']) 
    df = df.set_index('Timestamp') 
    df = df.resample('h').agg({'Power (MW)': 'mean','Press (psig)': 'mean', 'Temp (°F)': 'mean', 'PowerSwing (MW)': 'mean'})
    df = df.reset_index()
    logger.info(f'Aggregated 30 min interval data to hourly data: \n{df.head()}') 

    # Calculate the enthalpy using the IAPWS97 standard
    df = calculate_enthalpy_dataframe(df)
    logger.info(f'Finished Calculating enthalpy using the IAPWS97 standard: \n{df.head()}')

    # Chart 1 Preparation
    logger.info('Preparing Chart 1...')
    filename_1 = chart_1(df)
    logger.info(f'Finished with Chart 1: {filename_1}. Review on Browser. File saved in the charts folder.')

    # Chart 2 Preparation
    logger.info('Preparing Chart 2 (multiple charts)...')
    filename_2_1 = chart_2_3d(df)
    filename_2_2 = chart_2_2d(df)
    filename_2_3 = chart_2_alternate(df)
    logger.info(f'Finished creating all charts for Chart 2:\n{filename_2_1}\n{filename_2_2}\n{filename_2_3}\nClickable HTML files are all saved in the charts folder. For further details please refer to the README.md file.')
    logger.info('All tasks completed successfully. Script finished...\n\n')

