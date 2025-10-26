from dash import Input, Output, callback, ctx
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def register_callbacks(app):

    df = pd.read_csv('data/portfolio.csv')

    df['total_value'] = df['buy_price'] * df['quantity']
    df['buy_date'] = pd.to_datetime(df['buy_date'])

    @callback (
        Output('line_total_plot', 'figure'),
        Output("btn-1d", "className"),
        Output("btn-1w", "className"),
        Output("btn-1m", "className"),
        Output("btn-6m", "className"),
        Output("btn-1y", "className"),
        Output("btn-all", "className"),
        [
            Input('btn-1d', 'n_clicks'),
            Input("btn-1w", "n_clicks"),
            Input("btn-1m", "n_clicks"),
            Input("btn-6m", "n_clicks"),
            Input("btn-1y", "n_clicks"),
            Input("btn-all", "n_clicks")
        ]
    )

    def update_line_chart(btn_1d, btn_1w, btn_1m, btn_6m, btn_1y, btn_all):

        triggered_id = ctx.triggered_id or "btn-all"

        today = datetime.today()

        if triggered_id == "btn-1d":
            start_date = today - timedelta(days=1)
        elif triggered_id == "btn-1w":
            start_date = today - timedelta(weeks=1)
        elif triggered_id == "btn-1m":
            start_date = today - timedelta(days=30)
        elif triggered_id == "btn-6m":
            start_date = today - timedelta(days=180)
        elif triggered_id == "btn-1y":
            start_date = today - timedelta(days=700)
        else:
            start_date = df["buy_date"].min()

        filtered_df = df[df['buy_date'] >= start_date].copy()
        filtered_df = filtered_df.sort_values('buy_date')
        filtered_df['cumulative_total'] = filtered_df['total_value'].cumsum()

        fig_total_line = px.line(filtered_df, 
                        x = 'buy_date', 
                        y = 'cumulative_total', 
                        markers=True,
                        )
        fig_total_line.update_traces(
            line=dict(color='#039be5', width=5),
            fill='tozeroy',
            fillcolor="rgba(3, 155, 229, 0.3)",
            hovertemplate="Date: %{x}<br>Total: %{y}<extra></extra>",
            hoverlabel=dict(
                font_family="Markazi Text",
                font_size=20,
            )
            )
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
            plot_bgcolor="#303655",
            paper_bgcolor="#303655",
            )

        fig_total_line.update_yaxes(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.2)',
            side='right',
            gridwidth=1,
            tickfont=dict(size=16, color='#f2f2f2')
        )

        fig_total_line.update_xaxes(
            showgrid=False,
            linecolor='grey',
            tickfont=dict(size=16, color='#f2f2f2')
        )

        buttons = ["btn-1d", "btn-1w", "btn-1m", "btn-6m", "btn-1y", "btn-all"]
        classes = ['time-btn active' if btn == triggered_id  else 'time-btn' for btn in buttons]

        return [fig_total_line] + classes