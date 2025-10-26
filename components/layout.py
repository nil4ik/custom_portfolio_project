from dash import html, dcc, dash_table
import pandas as pd
import plotly.express as px

#################################################################################


df = pd.read_csv('data/portfolio.csv')

df['total_value'] = df['buy_price'] * df['quantity']
df_total = df.groupby('buy_date')['total_value'].sum().reset_index()
df_total = df.sort_values('buy_date')
df_total['cumulative_total'] = df_total['total_value'].cumsum()

##################################################################################

fig_total_pie = px.pie(
    df_total, 
    values= 'total_value', 
    names = 'category',
    hole= .3)

fig_total_pie.update_traces(
    hoverinfo = 'label+percent+name', 
    textinfo ='percent', 
    textfont=dict(color='white'),
    hovertemplate= "<b>%{label}</b><br>" + "Total: %{value}$<br>" + "Percentage: %{percent}",
    hoverlabel=dict(
        font_family="Markazi Text",
        font_size=20,
    )
    )
fig_total_pie.update_layout(
    legend=dict(orientation = 'v',yanchor="top", font=dict(size=14, color="#f2f2f2")),
    plot_bgcolor="#303655",
    paper_bgcolor="#303655"
    )

#################################################################################

time_buttons = html.Div([
    html.Button("1D", id="btn-1d", n_clicks=0, className="time-btn"),
    html.Button("1W", id="btn-1w", n_clicks=0, className="time-btn"),
    html.Button("1M", id="btn-1m", n_clicks=0, className="time-btn"),
    html.Button("6M", id="btn-6m", n_clicks=0, className="time-btn"),
    html.Button("1Y", id="btn-1y", n_clicks=0, className="time-btn"),
    html.Button("ALL", id="btn-all", n_clicks=0, className="time-btn active")
], className="time-filter")

#################################################################################

table = html.Div(
    dash_table.DataTable(
        id='portfolio-table',
        columns=[
            {"name": "Name", "id": "name"},
            {"name": "Category", "id": "category"},
            {"name": "Buy Price", "id": "buy_price", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Quantity", "id": "quantity", "type": "numeric"},
            {"name": "Buy Date", "id": "buy_date", "type": "datetime"},
            {"name": "Total Value", "id": "total_value", "type": "numeric", "format": {"specifier": ".2f"}}
        ],
        data=df.to_dict('records'),
        sort_action='native', 
        style_as_list_view=True,
        page_action='native',
        page_current=0,
        page_size=20
    ),
    className = 'portfolio_table_css'
)

#################################################################################

def serve_layout():
    return html.Div([
        html.H1('Custom portfolio dashboard', className = 'header'),
        html.Div(
            className='info_panel',
            children=[
                html.Div('Total Value: 1234$', className='info_box'),
                html.Div('Most expensive item: 1554$', className='info_box'),
                html.Div('The cheapest item: 3421$', className='info_box'),
                html.Div('Average item price: 12323414$', className='info_box'),
                html.Div('First bought: Rolex 2012 gold', className='info_box'),
                html.Div('Last bought: buggati 2021', className='info_box'),
                html.Div('Number of Assets: 4331', className='info_box'),
                html.Div('Category breakdown: crypto', className='info_box')
            ],
        ),
        html.Div(time_buttons, className='time_buttons_container'),
        html.Div([
            html.Div([
                dcc.Graph(id = 'line_total_plot', config={'displayModeBar':False})
                ], className='graph_container_line'),
            html.Div([dcc.Graph(id = 'pie_total_plot', figure = fig_total_pie, config={'displayModeBar':False})], className= 'graph_container_pie')],
            className='graph_containers_total'),

        html.Div([
            html.H2('Portfolio details', className='portfolio_details_h2'),
            html.Div(table, className = 'table_style_container')], 
            className='container_table_general')
    ])