# This is a TOMO1S12V2I class Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#Import pandas
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# make sure figures appear inline in Ipython Notebook
# matplotlib inline
# Press the green button in the gutter to run the script.
df = pd.read_csv('/home/goo/github/pyTomo/goo2.csv',sep=';')

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Scatter(x=df['Time'], y=df['I2'], name="I2"),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(x=df['Time'], y=df['I1'], name="I1"),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V1'], name="V1"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V2'], name="V2"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V3'], name="V3"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V4'], name="V4"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V5'], name="V5"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V6'], name="V6"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V7'], name="V7"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V8'], name="V8"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V9'], name="V9"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V10'], name="V10"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V11'], name="V11"),
    secondary_y=True,
)
fig.add_trace(
    go.Scatter(x=df['Time'], y=df['V12'], name="V12"),
    secondary_y=True,
)


# Add figure title
fig.update_layout(
    title_text="TomoGraphe Result 23/09/2024"
)
fig.update_yaxes(range = [-0.1,0.1], secondary_y=False)
fig.update_yaxes(range = [-2000,2000], secondary_y=True)

# Set x-axis title
fig.update_xaxes(title_text="Time")

# Set y-axes titles
fig.update_yaxes(title_text="mA", secondary_y=False)
fig.update_yaxes(title_text="mV", secondary_y=True)
fig.write_html("goOHm.html")
fig.show()