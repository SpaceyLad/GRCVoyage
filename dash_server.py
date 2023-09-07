import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from flask import Flask, render_template
import pandas as pd
import config as conf

# Flask app
server = Flask(__name__)

# Dash app
app = dash.Dash(__name__, server=server, url_base_pathname="/dashboard/")
html.Div(id="hidden-div", style={"display": "none"})

# Define colors for each risk rating
color_map = {
    "Low": "green",
    "Medium": "yellow",
    "High": "orange",
    "Critical": "red"
}
hover_data = ["Risk ID", "Risk Description", "Last Review Date", "Comments"]


def figures(df):
    vuln_fig = px.bar(df,
                      x="Risk Rating",
                      title="Numbers of vulnerabilities",
                      hover_data=hover_data,
                      color="Risk Rating",
                      color_discrete_map=color_map,
                      )

    stat_fig = px.bar(df,
                      x="Risk Status",
                      title="Status",
                      hover_data=hover_data,
                      color="Risk Rating",
                      color_discrete_map=color_map,
                      )
    assigned_fig = px.bar(df,
                          x="Assigned To",
                          title="Assigned to",
                          hover_data=hover_data,
                          color="Risk Rating",
                          color_discrete_map=color_map,
                          )
    return vuln_fig, stat_fig, assigned_fig


def refresh_dashboard():
    # Load all data
    df = pd.read_csv(conf.cases_file)
    vuln_fig, stat_fig, assigned_fig = figures(df)

    # Layout for the Dash app
    buttons = html.Div([
        html.Button(year, id=f'btn-{year}', n_clicks=0) for year in range(2020, 2028)
    ])
    app.layout = html.Div([
        html.Div(id="current-year", style={"display": "none"}, children="2020"),
        html.Div(id="link-container"),
        buttons,
        dcc.Location(id="url", refresh=False),
        dcc.Graph(id="vuln-chart", figure=vuln_fig),
        dcc.Graph(id="stat-chart", figure=stat_fig),
        dcc.Graph(id="assigned-chart", figure=assigned_fig),
    ])


@app.callback(
    [
        Output("vuln-chart", "figure"),
        Output("stat-chart", "figure"),
        Output("assigned-chart", "figure"),
        Output("current-year", "children")
    ],
    [Input(f'btn-{year}', 'n_clicks') for year in range(2020, 2028)]
)
def update_graphs(*btns):
    # Get the direct button that was triggered, not the whole tuple list.
    # Tuple list cannot be reset, so it is difficult to work with.
    # This took too long..
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Get the id of the button that triggered the callback
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Extract the year from the button's ID
    year_clicked = int(button_id.split('-')[1])

    if not year_clicked:
        raise dash.exceptions.PreventUpdate

    df = pd.read_csv(conf.cases_file)

    # Filter the data based on year
    df = df[df['Last Review Date'].str.contains(str(year_clicked))]
    vuln_fig, stat_fig, assigned_fig = figures(df)

    return vuln_fig, stat_fig, assigned_fig, str(year_clicked)


@app.callback(
    Output("link-container", "children"),
    [Input("vuln-chart", "clickData"),
     Input("stat-chart", "clickData"),
     Input("assigned-chart", "clickData")]
)
def display_link(vulnData, statData, assignedData):
    # Check which Input triggered the callback
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Initialize clickData as None
    clickData = None

    # Filter whick table gave the data
    if input_id == "vuln-chart":
        clickData = vulnData
    elif input_id == "stat-chart":
        clickData = statData
    elif input_id == "assigned-chart":
        clickData = assignedData

    if clickData:
        # Get the category of the clicked bar
        risk_id = clickData["points"][0]["customdata"][0]  # Accessing 'Risk ID' from hover_data
        # Create a link based on the clicked bar
        link = html.A(f"Details for Risk ID: {risk_id}", href=f"/vuln/{risk_id}")
        return link

    return dash.no_update


@server.route("/vuln/<risk_id>")
def show_vuln_details(risk_id):
    df = pd.read_csv(conf.cases_file)

    # Filter dataframe for the given risk_id
    filtered_df = df[df["Risk ID"] == risk_id]

    # Convert the filtered dataframe to an HTML table
    table_html = filtered_df.to_html(classes="table table-striped", index=False)

    # TODO: Calculate the risk in the matrix and print in header.
    # risk_matrix(filtered_df[df["Likelihood"]],filtered_df[df["Risk Rating"]])
    # TODO: Generate a short AI summary with GPT with a button.
    # gpt_summary()

    # Render the table using the HTML template
    return render_template("vuln_details.html", table_html=table_html)


def risk_matrix(risk, impact):
    def convert(number):
        if number == "low":
            number = 1
        elif number == "medium":
            number = 2
        elif number == "high":
            number = 3
        elif number == "critical":
            number = 4
        return number

    risk = convert(risk)
    impact = convert(impact)
    sum = risk * impact

    if sum < 4:
        final_risk = "low"
    elif 5 < sum < 8:
        final_risk = "Medium"
    elif 9 < sum < 12:
        final_risk = "High"
    elif sum == 16:
        final_risk = "Critical"

    # |     low|  Medium|     High|Critical|
    # |       4|       8|       12|      16|Critical
    # |       3|       6|        9|      12|High
    # |       2|       4|        6|       8|Medium
    # |       1|       2|        3|       4|low

    print(final_risk)

    return final_risk


def gpt_summary():
    print("Ey")
