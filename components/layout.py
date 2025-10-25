from dash import html, dcc, dash_table
import pandas as pd
import plotly.express as px

df = pd.read_csv('data/portfolio.csv')

df['total_value'] = df['buy_price'] * df['quantity']
df_total = df.groupby('buy_date')['total_value'].sum().reset_index()
df_total = df.sort_values('buy_date')
df_total['cumulative_total'] = df_total['total_value'].cumsum()

fig_total_line = px.line(df_total, 
                    x = 'buy_date', 
                    y = 'cumulative_total', 
                    markers=True,
                    )
fig_total_line.update_traces(mode = 'lines', line={'width': 5})
fig_total_line.update_layout(
    legend={'font': {'size': 16}},
    xaxis_title=None, yaxis_title=None,
    title={
        'font': {'size': 30},
        'x': 0.5,
        'xanchor': 'center'
        },
    xaxis=dict(tickfont=dict(size=20)),
    yaxis=dict(tickfont=dict(size=20)),
    )

fig_total_pie = px.pie(
    df_total, 
    values= 'total_value', 
    names = 'category',
    hole= .3)

fig_total_pie.update_traces(hoverinfo = 'label+percent+name', textinfo ='none')
fig_total_pie.update_layout(
    legend={'font': {'size': 16}}
    )

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

def serve_layout():
    return html.Div([
        html.H1('Custom portfolio dashboard', className = 'header'),

        html.Div([
            dcc.Graph(id = 'line_total_plot', figure = fig_total_line),
            dcc.Graph(id = 'pie_total_plot', figure = fig_total_pie)],
            className='graph_container_total'),

        html.Div([
            html.H2('Portfolio details', style = {'textAlign':'center', 'fontSize':'42px'}),
            html.Div(table, className = 'table_style_container')], 
            className='container_table_general')
    ])