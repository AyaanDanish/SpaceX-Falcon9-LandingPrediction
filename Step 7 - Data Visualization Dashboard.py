# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

options_list = [
    {"label": site, "value": site} for site in spacex_df["Launch Site"].unique()
]
options_list.insert(0, {"label": "All Sites", "value": "ALL"})
marks_dict = {num: f"{num}" for num in range(0, 100001, 500) if num <= 10000}

# Create an app layout
app.layout = html.Div(
    style={"font-family": "Helvetica"},
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        dcc.Dropdown(
            id="site-dropdown",
            options=options_list,
            value="ALL",
            placeholder="- Select a Launch Site -",
            searchable=True,
        ),
        html.Br(),
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks=marks_dict,
            value=[min_payload, max_payload],
        ),
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ],
)


@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        filtered_df = spacex_df.groupby("Launch Site")["class"].sum().reset_index()
        fig = px.pie(
            filtered_df,
            values="class",
            names="Launch Site",
            title="Total Successful Launches by Launch Site",
        )
        return fig
    else:
        filtered_df = (
            spacex_df[spacex_df["Launch Site"] == entered_site]
            .groupby(["class"])["class"]
            .value_counts()
            .reset_index()
        )
        fig = px.pie(
            filtered_df,
            values="count",
            names="class",
            title="Total Successful Launches by Launch Site",
        )
        return fig


# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# You can add this part once you've implemented the scatter chart.
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_plot(entered_site, payload_range):
    if entered_site == "ALL":
        filtered_df = spacex_df[
            (spacex_df["Payload Mass (kg)"] >= payload_range[0])
            & (spacex_df["Payload Mass (kg)"] <= payload_range[1])
        ]
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
        )
        return fig
    else:
        filtered_df = spacex_df[
            (spacex_df["Payload Mass (kg)"] >= payload_range[0])
            & (spacex_df["Payload Mass (kg)"] <= payload_range[1])
            & (spacex_df["Launch Site"] == entered_site)
        ]

        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
        )
        return fig


# Run the app
if __name__ == "__main__":
    app.run_server(port=8050)
