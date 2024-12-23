import streamlit as st , pandas as pd
import plotly.graph_objects as go, plotly.express as px
# from prepare_data import prepare_data 
import sys
import os

file_url = f"https://docs.google.com/uc?export=download&id=1pjaVbBfL4K6rNL9sJqwtH9D_SHTpK_6_"
## helper functions 

def prepare_data(level=None):
    woreda = pd.read_excel(file_url, sheet_name="Woreda Activities")
    woreda["Level"] = "Woreda level"
    region = pd.read_excel(file_url, sheet_name="Region Activities")
    region["Level"] = "Regional level"
    national = pd.read_excel(file_url, sheet_name="National Activities")
    national["Level"] = "National level"

    df = pd.DataFrame()
    for d in [woreda, region, national]:
        d.columns = d.columns.str.lower()
        df = pd.concat([d, df], axis=0)

    pmap = {
        'Availability of essential inputs ensured': "PO3-Inputs & HMIS",
        'Improved primary health care governance': "PO1-Governance",
        'Improved efficiencies and resource mobilization for health': "PO2-Financing",
        'Cross cutting': "Cross cutting"
    }
    df["po key"] = df["primary outcome"].map(pmap)
    print(df["level"].unique())
    if level == None:
        return df
    elif level == "Activity":
        filtered_rows = (df["level"] == "Woreda level") | (df["level"] =="Regional level")
        return df.loc[filtered_rows,:]

# Create a progress bar using Plotly
def custom_progress_bar(value):
    if value >= 85:
        color = 'green'
    elif value >= 70:
        color = 'yellow'
    else:
        color = 'red'
    value = int(max(0, min(100, value)))
    st.components.v1.html(f"""
    <div style="position: relative; width: 100%; background-color: lightgray; border-radius: 5px; overflow: hidden;">
        <div style="width: {value}%; background-color: {color}; height: 10px; border-radius: 5px;"></div>
        <div style="position: absolute; width: 100%; top: 0; left: 0; height: 10px; display: flex; align-items: center; justify-content: center; color: black; font-weight: bold; font-size: 10px;">
            {value}%
        </div>
    </div>
    """, height=20)

df = prepare_data(level="Activity")

# Create filters 
st.write("Filter controls")
selected_il = st.sidebar.multiselect("Implementation level:", options=df['level'].unique())
selected_po = st.sidebar.multiselect("Primary outcome:", options=df['po key'].unique())
filtered_df = df.copy()  # Start with a copy of the original DataFrame
if selected_il:
    filtered_df = filtered_df[filtered_df['level'].isin(selected_il)]
if selected_po:
    filtered_df = filtered_df[filtered_df['po key'].isin(selected_po)]

# Activity to-date performance
col1, col3, col2 = st.columns([1,0.1, 1])

with col1:
    st.write("Indicator to-date performance")
    if not filtered_df.empty:
        average_score = filtered_df['performance (indicator todate)'].mean()
    else:
        average_score = 0  # Handle the case when no rows match the filter

    # st.write(f"Average Score for selected filters: {average_score:.2f}")
    st.markdown("---")
    with st.container():
        # Create the interactive gauge chart using Plotly
        if average_score <= 70:
            gauge_color = "red"
        elif 70 < average_score <= 85:
            gauge_color = "yellow"
        elif average_score > 85:
            gauge_color = "green"

        # Create the interactive gauge chart using Plotly with conditional formatting
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_score,
            title={'text': "Average Score", 'font': {'size': 12}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "darkblue"},
                # 'bar': {'color': gauge_color},
                'bar': {'color': 'blue'},  # Bar color changes based on average score
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 70], 'color': "red"},
                    {'range': [70, 85], 'color': "yellow"},
                    {'range': [85, 100], 'color': "green"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.5,
                    'value': average_score
                }
            }
        ))

        # Show the improved gauge chart in Streamlit
        fig.update_layout(
            yaxis_title= None, 
            xaxis_title= None, 
            margin=dict(l=20, r=20, t=10, b=10),
            height=400,
            width = 400)
        config={'displayModeBar': False, 'showlegend': False}
        # config={'displayModeBar': True, 'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'resetScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian']}
        st.write("Overall to-date indicator progress")
        custom_progress_bar(average_score)
        # st.plotly_chart(fig, use_container_width=True, config=config)

    # Define a function to assign colors based on the average value
    def assign_color(value):
        if value < 70:
            return 'red'
        elif 70 > value <= 85:
            return 'yellow'
        else:
            return 'green'

    # chart by primary outcome 
    avg_df_po = filtered_df.groupby('po key', as_index=False)['performance (indicator todate)'].mean()
    avg_df_po['color'] = avg_df_po['performance (indicator todate)'].apply(assign_color)

    # Create a horizontal bar chart using Plotly Express
    fig = px.bar(avg_df_po, 
                x='performance (indicator todate)', 
                y='po key', 
                text='performance (indicator todate)', 
                orientation='h', 
                color='color',
                color_discrete_map={
                    'red': 'red',
                    'yellow': 'yellow',
                    'green': 'green'
                },
                labels={'performance (indicator todate)': 'Average Value', 'region': 'Region'},
                # title= 'Average of indicator to-date performance by primary outcome'
                )
 
      # Update layout for better appearance
    fig.update_traces(texttemplate='%{text:.0f}', textfont_size=10, textposition='outside')
    config={'displayModeBar': False, 'showlegend': False}
    fig.update_layout(
        yaxis_title= None, 
        xaxis_title= None, 
        margin=dict(l=20, r=20, t=10, b=10),
        width = 200,
        height = 90,
        showlegend = False,
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0,100]) 
        # yaxis=dict(showticklabels=False, showgrid=False, zeroline=False)
    )  

        # Display the bar chart in Streamlit
    st.write("Average indicator to-date performance by primary outcome")
    st.plotly_chart(fig, use_container_width=True, config=config)

    #bar chart performance by region 
    avg_df = filtered_df.groupby('region', as_index=False)['performance (indicator todate)'].mean()
    avg_df['color'] = avg_df['performance (indicator todate)'].apply(assign_color)

    # Create a horizontal bar chart using Plotly Express
    fig = px.bar(avg_df, 
                x='performance (indicator todate)', 
                y='region', 
                text='performance (indicator todate)', 
                orientation='h', 
                color='color',
                color_discrete_map={
                    'red': 'red',
                    'yellow': 'yellow',
                    'green': 'green'
                },
                labels={'performance (indicator todate)': 'Average Value', 'region': 'Region'},
                # title='Average of indicator to-date performance by region'
            )

    # Update layout for better appearance
    fig.update_traces(texttemplate='%{text:.0f}', textfont_size=10, textposition='outside')
    config={'displayModeBar': False, 'showlegend': False}
    fig.update_layout(
        yaxis_title= None, 
        xaxis_title= None, 
        margin=dict(l=20, r=20, t=10, b=10),
        height = 150,
        width = 200,
        showlegend = False,
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0,100]) )  

    # chart indicator to-date by region
    st.write("Average indicator to-date performance by region")
    st.plotly_chart(fig, use_container_width=True, config=config)

with col2:
    st.write("Indicator YTD performance")
    if not filtered_df.empty:
        average_score = filtered_df['performance (indicator ytd)'].mean()
    else:
        average_score = 0  # Handle the case when no rows match the filter

    # st.write(f"Average Score for selected filters: {average_score:.2f}")
    st.markdown("---")
    with st.container():
        # Create the interactive gauge chart using Plotly
        if average_score <= 70:
            gauge_color = "red"
        elif 70 < average_score <= 85:
            gauge_color = "yellow"
        elif average_score > 85:
            gauge_color = "green"

        # Create the interactive gauge chart using Plotly with conditional formatting
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_score,
            title={'text': "Average Score", 'font': {'size': 12}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "darkblue"},
                # 'bar': {'color': gauge_color},
                'bar': {'color': 'blue'},  # Bar color changes based on average score
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 70], 'color': "red"},
                    {'range': [70, 85], 'color': "yellow"},
                    {'range': [85, 100], 'color': "green"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.5,
                    'value': average_score
                }
            }
        ))

        # Show the improved gauge chart in Streamlit
        fig.update_layout(
            yaxis_title= None, 
            xaxis_title= None, 
            margin=dict(l=20, r=20, t=10, b=0),
            height=400,
            width = 400)
        config={'displayModeBar': False, 'showlegend': False}
        # config={'displayModeBar': True, 'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'resetScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian']}
        st.write("Overall to-date indicator progress")
        custom_progress_bar(average_score)
        # st.plotly_chart(fig, use_container_width=True, config=config)

    # Define a function to assign colors based on the average value
    def assign_color(value):
        if value < 70:
            return 'red'
        elif 70 > value <= 85:
            return 'yellow'
        else:
            return 'green'

    # chart by primary outcome 
    avg_df_po = filtered_df.groupby('po key', as_index=False)['performance (indicator ytd)'].mean()
    avg_df_po['color'] = avg_df_po['performance (indicator ytd)'].apply(assign_color)

    # Create a horizontal bar chart using Plotly Express
    fig = px.bar(avg_df_po, 
                x='performance (indicator ytd)', 
                y='po key', 
                text='performance (indicator ytd)', 
                orientation='h', 
                color='color',
                color_discrete_map={
                    'red': 'red',
                    'yellow': 'yellow',
                    'green': 'green'
                },
                labels={'performance (indicator ytd)': 'Average Value', 'region': 'Region'},
                # title= 'Average of indicator to-date performance by primary outcome'
                )
 
      # Update layout for better appearance
    fig.update_traces(texttemplate='%{text:.0f}', textfont_size=10, textposition='outside')
    config={'displayModeBar': False, 'showlegend': False}
    fig.update_layout(
        yaxis_title= None, 
        xaxis_title= None, 
        margin=dict(l=20, r=20, t=10, b=10),
        width = 200,
        height = 90,
        showlegend = False,
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0,100]) 
        # yaxis=dict(showticklabels=False, showgrid=False, zeroline=False)
    )  

        # Display the bar chart in Streamlit
    st.write("Average indicator YTD performance by primary outcome")
    st.plotly_chart(fig, use_container_width=True, config=config)

    #bar chart performance by region 
    avg_df = filtered_df.groupby('region', as_index=False)['performance (indicator ytd)'].mean()
    avg_df['color'] = avg_df['performance (indicator ytd)'].apply(assign_color)

    # Create a horizontal bar chart using Plotly Express
    fig = px.bar(avg_df, 
                x='performance (indicator ytd)', 
                y='region', 
                text='performance (indicator ytd)', 
                orientation='h', 
                color='color',
                color_discrete_map={
                    'red': 'red',
                    'yellow': 'yellow',
                    'green': 'green'
                },
                labels={'performance (indicator ytd)': 'Average Value', 'region': 'Region'},
                # title='Average of indicator to-date performance by region'
            )

    # Update layout for better appearance
    fig.update_traces(texttemplate='%{text:.0f}', textfont_size=10, textposition='outside')
    config={'displayModeBar': False, 'showlegend': False}
    fig.update_layout(
        yaxis_title= None, 
        xaxis_title= None, 
        margin=dict(l=20, r=20, t=10, b=10),
        height = 150,
        width = 200,
        showlegend = False,
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0,100]) )  

    # chart indicator to-date by region
    st.write("Average indicator YTD performance by region")
    st.plotly_chart(fig, use_container_width=True, config=config)


