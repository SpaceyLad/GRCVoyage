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
    "Medium": "orange",
    "High": "red"
}
hover_data = ["Risk ID", "Risk Description", "Last Review Date", "Comments"]


def refresh_dashboard():

    # Load data
    df = pd.read_csv(conf.cases_file)

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

    # Layout for the Dash app
    buttons = html.Div([
        html.Button(year, id=f'btn-{year}', n_clicks=0) for year in range(2020, 2028)
    ])
    app.layout = html.Div([
        buttons,  # Add the buttons here
        html.Div(id="link-container"),
        dcc.Location(id="url", refresh=False),
        dcc.Graph(id="vuln-chart", figure=vuln_fig),
        dcc.Graph(id="stat-chart", figure=stat_fig),
        dcc.Graph(id="assigned-chart", figure=assigned_fig),
    ])


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

    # Render the table using the HTML template
    return render_template("vuln_details.html", table_html=table_html)
