from dash import html, dcc, dash_table
import pandas as pd
import plotly.express as px

df = pd.read_csv('data/portfolio.csv')

df['total_value'] = df['buy_price'] * df['quantity']
df_total = df.groupby('buy_date')['total_value'].sum().reset_index()
df_total = df.sort_values('buy_date')
df_total['cumulative_total'] = df_total['total_value'].cumsum()

total_fig = px.line(df_total, 
                    x = 'buy_date', 
                    y = 'cumulative_total', 
                    markers=True,
                    ).update_layout(
                        xaxis_title=None, 
                        yaxis_title=None,
                    )

def server_layout():
    return html.Div([
        html.H1('Custom portfolio dashboard', className = 'header'),
        html.Div([
            html.H1('Portfolio Total Value', style = {'textAlign':'center'}),
            dcc.Graph(id = 'line_total_plot', figure = total_fig)],
            className='graph_container_total')
    ])