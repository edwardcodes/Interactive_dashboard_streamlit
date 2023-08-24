import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Setting page configuration
st.set_page_config(page_title="SuperStore!!!", page_icon=":tada:", layout="wide")
st.title(":bar_chart: Sample SuperStore App")

# To make the title at the top corner of the page
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# Creating uploading button to upload files
upload_file = st.file_uploader("Upload your data", type=['csv','txt','xlsx','xls'])
if upload_file is not None:
    # Reading the uploaded file
    filename = upload_file.name
    st.write("You selected `%s`" % filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    # os.chdir(r"./Interactive_dashboard_streamlit")
    df = pd.read_csv("./Superstore_2023.csv", encoding="ISO-8859-1")

# Converting order date to datetime
df['Order Date'] = pd.to_datetime(df['Order Date'],format='mixed')

# Create columns
col1, col2 = st.columns(2)

# Getting start date and end date from orders
start_date = df['Order Date'].min()
end_date = df['Order Date'].max()
# print(start_date, end_date)

# Creating date filters for orders
with col1:
    startDate = pd.to_datetime(st.date_input("Start Date", start_date))
with col2:
    endDate = pd.to_datetime(st.date_input("End Date", end_date))

# Filtering data based on date selected
df = df[(df['Order Date'] >= startDate) & (df['Order Date'] <= endDate)].copy()

# Displaying Sidebar
st.sidebar.header("Choose your filters: ")

# Filtering data based on region
region = st.sidebar.multiselect(
    "Region",
    df['Region'].unique()
)
if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]

# Filtering data based on state
state = st.sidebar.multiselect('State', df2['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]

# Filtering data based on city
city = st.sidebar.multiselect('City', df3['City'].unique())

# Optimizing the working of filters
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df = df[df['State'].isin(state)]
elif state and city:
    filtered_df = df3[df3['State'].isin(state) & df3['City'].isin(city)]
elif region and state:
    filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state)]
elif city:
    filtered_df = df3[df3['City'].isin(city)]
else:
    filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]

# Creating charts for category and region sales
category_df = filtered_df.groupby(by=['Category'],as_index=False)['Sales'].sum()
# print(category_df)

with col1:
    st.subheader("Category Sales")
    fig = px.bar(category_df, x='Category', y='Sales', template='seaborn', text=[f'${x:,.2f}' for x in category_df['Sales']])
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region Sales")
    fig = px.pie(filtered_df, values='Sales', names='Region', hole=0.5)
    # hole (float) – Sets the fraction of the radius to cut out of the pie.Use this to make a donut chart.
    fig.update_traces(text=filtered_df['Region'], textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

# Download data from above chart as CSV file
cl1, cl2 = st.columns(2)
with cl1:
    with st.expander('Category_ViewData'):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Category Sales",
            data=csv,
            file_name='Category_Sales.csv',
            mime='text/csv',
            help='Click here to download the data as CSV file'
        )

with cl2:
    with st.expander('Region_viewData'):
        # grouping by region
        region = filtered_df.groupby(by=['Region'],as_index=False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap='Oranges'))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Region Sales",
            data=csv,
            file_name='Region_Sales.csv',
            mime='text/csv',
            help='Click here to download the data as CSV file'
        )


# Creating time-series chart
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Create tree map chart based on region, category and subcategory
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")