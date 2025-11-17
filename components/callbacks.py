from components.layout import dashboard_content, portfolio_content, transactions_content
from dash import Input, Output, callback, ctx, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import dash_bootstrap_components as dbc
import csv
from dash import html
from dash import dcc
from dash import no_update
import uuid


def load_portfolio_with_buttons():
    df = pd.read_csv('data/portfolio.csv')
    df["add"] = "➕"
    df["edit"] = "🖋️"
    df["delete"] = "❌"
    df["sell"] = "💲"
    return df.to_dict('records')

def load_history():
    df = pd.read_csv('data/portfolio_history.csv')
    return df.to_dict('records')


####################################################################################

def register_callbacks(app):

############################## tabs callback ######################################

    @callback(
        Output("page-content", "children"),
        Input("main-tabs", "active_tab")
    )
    def switch_tab(active_tab):
        if active_tab == "dashboard":
            return dashboard_content()
        elif active_tab == "portfolio":
            return portfolio_content()
        else:
            return transactions_content()

################################### Table update ###############################

    @callback(
        Output('portfolio-table', 'rowData'),
        Input('main-tabs', 'active_tab'),
        Input('data-refresh-trigger', 'data'),
        prevent_initial_call=False
    )
    def initialize_table(active_tab, refresh_trigger):
        if active_tab != 'portfolio':
            return no_update
            
        df = pd.read_csv('data/portfolio.csv')
        df["add"] = "➕"
        df["edit"] = "🖋️"
        df["delete"] = "❌"
        df["sell"] = "💲"
        return df.to_dict('records')
    
################################### History update ####################################

    @callback(
        Output('portfolio-history-table', 'rowData'),
        Input('main-tabs', 'active_tab'),
        Input('data-refresh-trigger', 'data'),
        prevent_initial_call=False
    )
    def initialize_history_table(active_tab, refresh_trigger):
        if active_tab != 'transactions':
            return no_update
            
        df_his = pd.read_csv('data/portfolio_history.csv')
        return df_his.to_dict('records')
    
################################### Info Panel #######################################

    @callback(
        Output('total-value-box', 'children'),
        Output('number-of-assets-box', 'children'),
        Output('most-expensive-box', 'children'),
        Output('average-price-box', 'children'),
        Output('popular-category-box', 'children'),
        Output('profit-loss-box', 'children'),
        Input('main-tabs', 'active_tab'),
        Input('data-refresh-trigger', 'data'),
        prevent_initial_call=False
    )
    def update_info_panel(active_tab, refresh_trigger):
        if active_tab != 'dashboard':
            return no_update, no_update, no_update, no_update, no_update, no_update
            
        df = pd.read_csv('data/portfolio.csv')
        df_his = pd.read_csv('data/portfolio_history.csv')

        if df.empty:
            return (
                [html.Span("Total Value:", className='info-text'), html.Br(), "0.00€"],
                [html.Span("Number of Assets:", className='info-text'), html.Br(), "0"],
                [html.Span("Most expensive item:", className='info-text'), html.Br(), "N/A"],
                [html.Span("Average buy price:", className='info-text'), html.Br(), "0€"],
                [html.Span("Most popular category:", className='info-text'), html.Br(), "N/A"],
                [html.Span("Total Profit/Loss:", className='info-text'), html.Br(), "N/A"],
            )
        
        if df_his.empty:
            return (
                [html.Span("Total Value:", className='info-text'), html.Br(), f"{total_value:,.2f}€"],
                [html.Span("Number of Assets:", className='info-text'), html.Br(), f"{number_of_assets:,.0f}"],
                [html.Span("Most expensive item:", className='info-text'), html.Br(), most_expensive_text],
                [html.Span("Average buy price:", className='info-text'), html.Br(), f"{average_price:,.2f}€"],
                [html.Span("Most popular category:", className='info-text'), html.Br(), popular_category_text],
                [html.Span("Total Profit/Loss:", className='info-text'), html.Br(), "N/A"],
            )
        
        total_value = df['total_value'].sum()

        number_of_assets = df.shape[0]

        most_expensive = df.loc[df['total_value'].idxmax()]
        most_expensive_text = f"{most_expensive['name']} ({most_expensive['total_value']:,.2f}€)"

        average_price = df['total_value'].mean()

        popular_category = df.groupby('category')['total_value'].sum().reset_index()
        popular_category = popular_category.loc[popular_category['total_value'].idxmax()]
        popular_category_text = f"{popular_category['category']} ({popular_category['total_value']:,.2f}€)"

        profit_loss = df_his['profit_loss'].sum()
        if profit_loss > 0:
            profit_color = 'green'
            profit_text = f"+{profit_loss:,.2f}€"
        elif profit_loss < 0:
            profit_color = 'red'
            profit_text = f"{profit_loss:,.2f}€"
        else:
            profit_color = 'white'
            profit_text = f"{profit_loss:,.2f}€"

        return (
            [html.Span("Total Value:", className='info-text'), html.Br(), f"{total_value:,.2f}€"],
            [html.Span("Number of Assets:", className='info-text'), html.Br(), f"{number_of_assets:,.0f}"],
            [html.Span("Most expensive item:", className='info-text'), html.Br(), most_expensive_text],
            [html.Span("Average buy price:", className='info-text'), html.Br(), f"{average_price:,.2f}€"],
            [html.Span("Most popular category:", className='info-text'), html.Br(), popular_category_text],
            [html.Span("Total Profit/Loss:", className='info-text'), html.Br(), html.Span(profit_text, style={'color': profit_color})],        
        )

################################## line plot #########################################

    @callback (
        Output('line_total_plot', 'figure'),
        Output("btn-1d", "className"),
        Output("btn-1w", "className"),
        Output("btn-1m", "className"),
        Output("btn-6m", "className"),
        Output("btn-1y", "className"),
        Output("btn-all", "className"),
        Input('main-tabs', 'active_tab'),
        Input('data-refresh-trigger', 'data'),
        Input('btn-1d', 'n_clicks'),
        Input("btn-1w", "n_clicks"),
        Input("btn-1m", "n_clicks"),
        Input("btn-6m", "n_clicks"),
        Input("btn-1y", "n_clicks"),
        Input("btn-all", "n_clicks"),
        prevent_initial_call=False
    )
    def update_line_chart(active_tab, refresh_trigger, btn_1d, btn_1w, btn_1m, btn_6m, btn_1y, btn_all):
        if active_tab != 'dashboard':
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update
            
        df = pd.read_csv('data/portfolio.csv')
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=24, color="#f2f2f2")
            )
            fig.update_layout(
                plot_bgcolor="rgba(255, 255, 255, 0.05)",
                paper_bgcolor="rgba(255, 255, 255, 0.05)",
                xaxis_visible=False,
                yaxis_visible=False
            )
            buttons = ["btn-1d", "btn-1w", "btn-1m", "btn-6m", "btn-1y", "btn-all"]
            classes = ['time-btn' for _ in buttons]
            return [fig] + classes
        
        df["buy_date"] = pd.to_datetime(df["buy_date"])
        
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
            start_date = today - timedelta(days=365)
        else:
            start_date = df["buy_date"].min()

        buttons = ["btn-1d", "btn-1w", "btn-1m", "btn-6m", "btn-1y", "btn-all"]
        classes = ['time-btn active' if btn == triggered_id else 'time-btn' for btn in buttons]

        df_grouped = df.groupby("buy_date", as_index=False)["total_value"].sum()
        df_grouped = df_grouped.sort_values("buy_date")
        
        df_grouped["cumulative_value"] = df_grouped["total_value"].cumsum()
        
        filtered_df = df_grouped[df_grouped["buy_date"] >= start_date].copy()

        if filtered_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No assets for the selected period.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="rgba(255, 255, 255, 0.7)")
            )
            fig.update_layout(
                plot_bgcolor="rgb(12, 25, 53)",
                paper_bgcolor="rgb(12, 25, 53)",
                xaxis_visible=False,
                yaxis_visible=False
            )
            return [fig] + classes

        fig_total_line = px.line(filtered_df, 
                        x='buy_date', 
                        y='cumulative_value',
                        markers=True)
        
        fig_total_line.update_traces(
            line=dict(color='#3b82f6', width=5),
            fill='tozeroy',
            hovertemplate="Date: %{x}<br>Total: %{y}<extra></extra>",
            hoverlabel=dict(font_family="Markazi Text", font_size=20)
        )
        
        fig_total_line.update_layout(
            legend={'font': {'size': 16}},
            xaxis_title=None, yaxis_title=None,
            title={'font': {'size': 30}, 'x': 0.5, 'xanchor': 'center'},
            xaxis=dict(tickfont=dict(size=20)),
            yaxis=dict(tickfont=dict(size=20)),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        fig_total_line.update_yaxes(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.2)',
            side='right',
            gridwidth=1,
            tickfont=dict(size=16, color='rgba(255, 255, 255, 0.7)')
        )

        fig_total_line.update_xaxes(
            showgrid=False,
            linecolor='grey',
            tickfont=dict(size=16, color='rgba(255, 255, 255, 0.7)')
        )

        return [fig_total_line] + classes

######################### Pie chart #############################################

    @callback(
        Output('pie_total_plot', 'figure'),
        Input('main-tabs', 'active_tab'),
        Input('data-refresh-trigger', 'data'),
        prevent_initial_call=False
    )
    def update_pie_chart(active_tab, refresh_trigger):
        if active_tab != 'dashboard':
            return no_update
            
        df = pd.read_csv('data/portfolio.csv')
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=24, color="rgba(255, 255, 255, 0.7)")
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            return fig
        
        df['total_value'] = df['buy_price'] * df['quantity']
        df_grouped = df.groupby('category')['total_value'].sum().reset_index()
        
        fig_total_pie = px.pie(
            df_grouped, 
            values='total_value', 
            names='category',
            hole=.3
        )

        fig_total_pie.update_traces(
            hoverinfo='label+percent+name', 
            textinfo='percent', 
            textfont=dict(color='rgba(255, 255, 255, 0.7)'),
            hovertemplate="<b>%{label}</b><br>Total: %{value}$<br>Percentage: %{percent}",
            hoverlabel=dict(font_family="Markazi Text", font_size=20)
        )
        
        fig_total_pie.update_layout(
            legend=dict(orientation='v', yanchor="top", font=dict(size=14, color="#f2f2f2")),
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        
        return fig_total_pie
    
################################# Add item button #################################################

    @callback(
        Output("modal-add-button", "is_open"),
        Input("open-add-item", "n_clicks"),
        State("modal-add-button", "is_open"),
    )
    def toggle_add_modal(n1, is_open):
        if n1:
            return not is_open
        return is_open
    
    @callback(
        Output("alert-add-item", "is_open"),
        Output("data-refresh-trigger", "data"),
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
        State("data-refresh-trigger", "data"),
        prevent_initial_call=True
    )
    def add_item(n, name, category, price, qty, buy_date, current_trigger):
        if not n:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        if not all([name, category, price, qty, buy_date]):
            return False, no_update, name, category, price, qty, buy_date
        
        if (float(price) <= 0) or (float(qty) <= 0):
            return False, no_update, name, category, price, qty, buy_date
        
        try:
            new_id = str(uuid.uuid4())
            total_value = float(price) * float(qty)
            
            new_item = {
                "id": new_id,
                "name": name,
                "category": category,
                "buy_price": float(price),
                "quantity": float(qty),
                "buy_date": buy_date,
                "total_value": total_value,
            }
            
            df = pd.read_csv("data/portfolio.csv")
            df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
            df.to_csv("data/portfolio.csv", index=False)
            
            history = pd.read_csv("data/portfolio_history.csv")
            new_transaction = {
                'transaction_id': str(uuid.uuid4()),
                'asset_id': new_id,
                'name': name,
                'category': category,
                'price': price,
                'quantity': qty,
                'date': buy_date,
                'total_value': total_value,
                'transaction_type': 'buy',
                'profit_loss': 0
            }
            history = pd.concat([history, pd.DataFrame([new_transaction])], ignore_index=True)
            history.to_csv("data/portfolio_history.csv", index=False)

            return True, current_trigger + 1, "", "", "", "", date.today().isoformat()
        
        except Exception as e:
            print(f"Error adding item {e}")
            return False, no_update, name, category, price, qty, buy_date

############################ Add more button ###########################################

    @callback(
        Output("modal-add-more", "is_open", allow_duplicate=True),
        Output("modal-add-more-header", "children"),
        Output("buy-date-add-more", "value"),
        Output("store-add-more-row", "data"),
        Input("portfolio-table", "cellClicked"),
        prevent_initial_call=True
    )
    def open_add_more_modal(cell_clicked):
        if not cell_clicked or cell_clicked.get("colId") != "add":
            return no_update, no_update, no_update, no_update

        row_id = cell_clicked.get("rowId")
        
        if not row_id:
            return no_update, no_update, no_update, no_update

        df = pd.read_csv("data/portfolio.csv")
        row_data = df[df['id'] == row_id]

        if row_data.empty:
            return no_update, no_update, no_update, no_update
        
        row_data = row_data.iloc[0]
        
        return (
            True,
            f"Buy more '{row_data.get('name', '')}'",
            date.today().isoformat(),
            row_id
        )

    @callback(
        Output("modal-add-more", "is_open", allow_duplicate=True),
        Output("data-refresh-trigger", "data", allow_duplicate=True),
        Input("confirm-add-more", "n_clicks"),
        State("price-add-more", "value"),
        State("qty-add-more", "value"),
        State("buy-date-add-more", "value"),
        State("store-add-more-row", "data"),
        State("data-refresh-trigger", "data"),
        prevent_initial_call=True
    )
    def add_more_item(n_clicks, price, qty, buy_date, row_id, current_trigger):
        if not n_clicks or row_id is None:
            return no_update, no_update
        
        if not all([price, qty, buy_date]):
            return no_update, no_update
        
        price_float = float(price)
        qty_float = float(qty)
        
        if (price_float <= 0) or (qty_float <= 0):
            return no_update, no_update

        try:
            df = pd.read_csv("data/portfolio.csv")
            row_data = df[df['id'] == row_id]
            
            if row_data.empty:
                return no_update, no_update
            
            row = row_data.iloc[0].to_dict()
            
            old_quantity = float(row["quantity"])
            new_quantity = old_quantity + qty_float
            
            old_total_value = float(row["total_value"])
            new_total_value = qty_float * price_float
            total_value = old_total_value + new_total_value
            
            avg_price = total_value / new_quantity

            df.loc[df['id'] == row_id, 'buy_price'] = avg_price
            df.loc[df['id'] == row_id, 'quantity'] = new_quantity
            df.loc[df['id'] == row_id, 'total_value'] = total_value
            
            df.to_csv("data/portfolio.csv", index=False)

            history = pd.read_csv("data/portfolio_history.csv")
            new_transaction = {
                'transaction_id': str(uuid.uuid4()),
                'asset_id': row_id,
                'name': row['name'],
                'category': row['category'],
                'price': price_float,
                'quantity': qty_float,
                'date': buy_date,
                'total_value': new_total_value,
                'transaction_type': 'buy',
                'profit_loss': 0
            }
            history = pd.concat([history, pd.DataFrame([new_transaction])], ignore_index=True)
            history.to_csv("data/portfolio_history.csv", index=False)

            return False, current_trigger + 1

        except Exception as e:
            print(f"Error adding more: {e}")
            return no_update, no_update

############################ Edit button ###############################################

    @callback(
        Output("modal-edit", "is_open", allow_duplicate=True),
        Output("name-edit", "value"),
        Output("category-edit", "value"),
        Output("store-edit-row", "data"),
        Input("portfolio-table", "cellClicked"),
        prevent_initial_call=True
    )
    def open_edit_modal(cell_clicked):
        if not cell_clicked or cell_clicked.get("colId") != "edit":
            return no_update, no_update, no_update, no_update

        row_id = cell_clicked.get("rowId")
        
        if not row_id:
            return no_update, no_update, no_update, no_update

        df = pd.read_csv("data/portfolio.csv")
        row_data = df[df['id'] == row_id]

        if row_data.empty:
            return no_update, no_update, no_update, no_update
        
        row_data = row_data.iloc[0]
        
        return (
            True,
            row_data.get("name", ""),         
            row_data.get("category", ""),  
            row_id
        )

    @callback(
        Output("modal-edit", "is_open", allow_duplicate=True),
        Output("data-refresh-trigger", "data", allow_duplicate=True),
        Input("confirm-edit", "n_clicks"),
        State("name-edit", "value"),
        State("category-edit", "value"),
        State("store-edit-row", "data"),
        State("data-refresh-trigger", "data"),
        prevent_initial_call=True
    )
    def confirm_edit(n_clicks, name, category, row_id, current_trigger):
        if not n_clicks or row_id is None:
            return no_update, no_update

        try:
            df = pd.read_csv("data/portfolio.csv")
            
            if df[df['id'] == row_id].empty:
                return no_update, no_update
            
            df.loc[df['id'] == row_id, 'name'] = name
            df.loc[df['id'] == row_id, 'category'] = category
            
            df.to_csv("data/portfolio.csv", index=False)

            history = pd.read_csv("data/portfolio_history.csv")
            history.loc[history['asset_id'] == row_id, 'name'] = name
            history.loc[history['asset_id'] == row_id, 'category'] = category
            history.to_csv("data/portfolio_history.csv", index=False)

            return False, current_trigger + 1

        except Exception as e:
            print(f"Error editing item: {e}")
            return no_update, no_update

############################ Delete button ###############################################

    @callback(
        Output("delete-modal", "is_open", allow_duplicate=True),
        Output("modal-delete-body", "children"),
        Output("store-delete-row", "data"),
        Input("portfolio-table", "cellClicked"),
        prevent_initial_call=True
    )
    def open_delete_modal(active_cell):
        if not active_cell or active_cell["colId"] != "delete":
            return no_update, no_update, no_update
        
        row_id = active_cell.get("rowId")

        if not row_id:
            return no_update, no_update, no_update
        
        df = pd.read_csv("data/portfolio.csv")
        row_data = df[df['id'] == row_id]

        if row_data.empty:
            return no_update, no_update, no_update

        row_data = row_data.iloc[0]
        item_name = row_data.get('name', 'this item')
        
        return True, f"Are you sure you want to delete '{item_name}'", row_id

    @callback(
        Output("delete-modal", "is_open", allow_duplicate=True),
        Output("data-refresh-trigger", "data", allow_duplicate=True),
        Input("confirm-delete", "n_clicks"),
        State("store-delete-row", "data"),
        State("data-refresh-trigger", "data"),
        prevent_initial_call=True
    )
    def confirm_delete(n_clicks, row_id, current_trigger):
        if not n_clicks or row_id is None:
            return no_update, no_update

        try:
            df = pd.read_csv("data/portfolio.csv")
            df = df[df['id'] != row_id]
            df.to_csv("data/portfolio.csv", index=False)
            
            history = pd.read_csv("data/portfolio_history.csv")
            history = history[history['asset_id'] != row_id]
            history.to_csv("data/portfolio_history.csv", index=False)
            
            return False, current_trigger + 1
        
        except Exception as e:
            print(f"Error deleting item: {e}")
            return True, no_update

############################ Sell button ###############################################

    @callback(
        Output("modal-sell", "is_open", allow_duplicate=True),
        Output("modal-sell-header", "children"),
        Output("date-sell", "value"),
        Output("store-sell-row", "data"),
        Input("portfolio-table", "cellClicked"),
        prevent_initial_call=True
    )
    def open_sell_modal(cell_clicked):
        if not cell_clicked or cell_clicked.get("colId") != "sell":
            return no_update, no_update, no_update, no_update
    
        row_id = cell_clicked.get("rowId")
        
        if not row_id:
            return no_update, no_update, no_update, no_update

        df = pd.read_csv("data/portfolio.csv")
        row_data = df[df['id'] == row_id]

        if row_data.empty:
            return no_update, no_update, no_update, no_update
        
        row_data = row_data.iloc[0]
        
        return (
            True,
            f"Sell '{row_data.get('name', '')}'",
            date.today().isoformat(),
            row_id
        )
    
    @callback(
        Output("modal-sell", "is_open", allow_duplicate=True),
        Output("data-refresh-trigger", "data", allow_duplicate=True),
        Input("confirm-sell", "n_clicks"),
        State("price-sell", "value"),
        State("quantity-sell", "value"),
        State("date-sell", "value"),
        State("store-sell-row", "data"),
        State("data-refresh-trigger", "data"),
        prevent_initial_call=True
    )
    def confirm_sell(n_clicks, price, qty, sell_date, row_id, current_trigger):
        if not n_clicks or row_id is None:
            return no_update, no_update
        
        if not all([price, qty, sell_date]):
            return no_update, no_update

        price = float(price)
        qty = float(qty)

        if (price <= 0) or (qty <= 0):
            return no_update, no_update

        try:
            df = pd.read_csv("data/portfolio.csv")
            row_data = df[df['id'] == row_id]

            if row_data.empty:
                return no_update, no_update
            
            row = row_data.iloc[0].to_dict()
            
            old_quantity = float(row["quantity"])
            old_price = float(row["buy_price"])

            if qty > old_quantity:
                return no_update, no_update
            
            sell_total_value = qty * price
            profit_loss = (price - old_price) * qty
            
            if qty == old_quantity:
                df = df[df['id'] != row_id]
            else:
                new_quantity = old_quantity - qty
                new_total_value = new_quantity * old_price
                
                df.loc[df['id'] == row_id, 'quantity'] = new_quantity
                df.loc[df['id'] == row_id, 'total_value'] = new_total_value
            
            df.to_csv("data/portfolio.csv", index=False)

            history = pd.read_csv("data/portfolio_history.csv")
            new_transaction = {
                'transaction_id': str(uuid.uuid4()),
                'asset_id': row_id,
                'name': row['name'],
                'category': row['category'],
                'price': price,
                'quantity': qty,
                'date': sell_date,
                'total_value': sell_total_value,
                'transaction_type': 'sell',
                'profit_loss': profit_loss
            }
            history = pd.concat([history, pd.DataFrame([new_transaction])], ignore_index=True)
            history.to_csv("data/portfolio_history.csv", index=False)

            return False, current_trigger + 1

        except Exception as e:
            print(f"Error {e}")
            return no_update, no_update