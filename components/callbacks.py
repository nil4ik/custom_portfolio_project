from dash import Input, Output, callback, ctx, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import dash_bootstrap_components as dbc
import csv
from dash import dcc
from dash import no_update

####################################################################################

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

        buttons = ["btn-1d", "btn-1w", "btn-1m", "btn-6m", "btn-1y", "btn-all"]
        classes = ['time-btn active' if btn == triggered_id  else 'time-btn' for btn in buttons]

        if filtered_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="There were no transactions for the selected period.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=24, color="#f2f2f2")
            )
            fig.update_layout(
                plot_bgcolor="#303655",
                paper_bgcolor="#303655",
                xaxis_visible=False,
                yaxis_visible=False
            )
            return [fig] + classes

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

        return [fig_total_line] + classes
    
################################# Add item button #################################################

    @callback(
        Output("modal-add-button", "is_open"),
        [Input("open-add-item", "n_clicks"), Input("close-add-item", "n_clicks")],
        [State("modal-add-button", "is_open")],
    )

    def toggle_add_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
    
    @callback(
        Output("alert-add-item", "is_open"),
        Output("name-input", "value"),
        Output("category-input", "value"),
        Output("price-input", "value"),
        Output("qty-input", "value"),
        Output("buy-date-input", "value"),
        Input("submit-item", "n_clicks"),
        State("name-input", "value"),
        State("category-input", "value"),
        State("price-input", "value"),
        State("qty-input", "value"),
        State("buy-date-input", "value"),
        prevent_initial_call=True
    )

    def add_item(n, name, category, price, qty, buy_date):
        if not all([name, category, price, qty, buy_date]):
            return False, name, category, price, qty, buy_date
        
        new_item = {
            "name": name, "category": category, 
            "buy_price":float(price), "quantity": float(qty),
            "buy_date": buy_date
        }

        with open("data/portfolio.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(list(new_item.values()))
        
        return True, "", "", "", "", date.today().isoformat()

############################ Edit button ###############################################



############################ Delete button ###############################################

    @callback(
        Output("delete-modal", "is_open", allow_duplicate=True),
        Output("modal-delete-body", "children"),
        Output("store-delete-row", "data"),
        Input("portfolio-table", "cellClicked"),
        State("portfolio-table", "rowData"),
        prevent_initial_call=True
    )
    def open_delete_modal(active_cell, rows):
        if not active_cell or active_cell["colId"] != "delete":
            return no_update, no_update, no_update
        
        row_idx = active_cell["rowIndex"]
        if row_idx >= len(rows):
            return no_update, no_update, no_update
        
        item_name = rows[row_idx].get('name', 'this item')
        return True, f"Are you sure you want to delete '{item_name}'?", row_idx


    @callback(
        Output("delete-modal", "is_open", allow_duplicate=True),
        Output("portfolio-table", "rowData", allow_duplicate=True),
        Input("confirm-delete", "n_clicks"),
        State("store-delete-row", "data"),
        State("portfolio-table", "rowData"),
        prevent_initial_call=True
    )
    def confirm_delete(n_clicks, row_idx, rows):
        if not n_clicks or row_idx is None or row_idx >= len(rows):
            return no_update, no_update, no_update

        try:
            rows.pop(row_idx)
            pd.DataFrame(rows).to_csv("data/portfolio.csv", index=False)
            return False, rows
        except Exception as e:
            print(f"Error deleting item: {e}")
            return True, no_update

############################ Sell button ###############################################