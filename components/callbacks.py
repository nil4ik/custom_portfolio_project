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

####################################################################################

def register_callbacks(app):

################################### Table update ###############################

    @callback(
        Output('portfolio-table', 'rowData'),
        Input('portfolio-table', 'id')
    )
    def initialize_table(_):
        df = pd.read_csv('data/portfolio.csv')
        
        df["add"] = "add"
        df["edit"] = "edit"
        df["delete"] = "delete"
        df["sell"] = "sell"
        
        return df.to_dict('records')
    
################################### History update ####################################

    @callback(
        Output('portfolio-history-table', 'rowData'),
        Input('portfolio-history-table', 'id')
    )
    def initialize_history_table(_):
        df_his = pd.read_csv('data/portfolio_history.csv')
        
        return df_his.to_dict('records')
    
################################### Info Panel #######################################33

    @callback(
        Output('total-value-box', 'children'),
        Output('number-of-assets-box', 'children'),
        Output('most-expensive-box', 'children'),
        Output('average-price-box', 'children'),
        Output('popular-category-box', 'children'),
        Input('portfolio-table', 'rowData')
    )

    def update_info_panel(row_data):
        df = pd.read_csv('data/portfolio.csv')

        if df.empty:
            return (
                [html.Span("Total Value:", className='info-text'), html.Br(), "0.00€"],
                [html.Span("Number of Assets:", className='info-text'), html.Br(), "0"],
                [html.Span("Most expensive item:", className='info-text'), html.Br(), "N/A"],
                [html.Span("Average buy price:", className='info-text'), html.Br(), "0€"],
                [html.Span("Most popular category:", className='info-text'), html.Br(), "N/A"],
            )
        
        total_value = df['total_value'].sum()

        number_of_assets = df['quantity'].sum()

        most_expensive = df.loc[df['total_value'].idxmax()]
        most_expensive_text = f"{most_expensive['name']} ({most_expensive['total_value']:,.2f}€)"

        average_price = df['total_value'].mean()

        popular_category = df.groupby('category')['total_value'].sum().reset_index()
        popular_category = popular_category.loc[popular_category['total_value'].idxmax()]

        popular_category_text = f"{popular_category['category']} ({popular_category['total_value']:,.2f}€)"

        return (
            [html.Span("Total Value:", className='info-text'), html.Br(), f"{total_value:,.2f}€"],
            [html.Span("Number of Assets:", className='info-text'), html.Br(), f"{number_of_assets:,.0f}"],
            [html.Span("Most expensive item:", className='info-text'), html.Br(), most_expensive_text],
            [html.Span("Average buy price:", className='info-text'), html.Br(), f"{average_price:,.2f}€"],
            [html.Span("Most popular category:", className='info-text'), html.Br(), popular_category_text],
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
        [
            Input('btn-1d', 'n_clicks'),
            Input("btn-1w", "n_clicks"),
            Input("btn-1m", "n_clicks"),
            Input("btn-6m", "n_clicks"),
            Input("btn-1y", "n_clicks"),
            Input("btn-all", "n_clicks"),
            Input("portfolio-table", "rowData")
        ]
    )
    def update_line_chart(btn_1d, btn_1w, btn_1m, btn_6m, btn_1y, btn_all, row_data):
        
        df = pd.read_csv('data/portfolio_history.csv')
        df["date"] = pd.to_datetime(df["date"])
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
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
            buttons = ["btn-1d", "btn-1w", "btn-1m", "btn-6m", "btn-1y", "btn-all"]
            classes = ['time-btn' for _ in buttons]
            return [fig] + classes
        
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
            start_date = df["date"].min()

        buttons = ["btn-1d", "btn-1w", "btn-1m", "btn-6m", "btn-1y", "btn-all"]
        classes = ['time-btn active' if btn == triggered_id else 'time-btn' for btn in buttons]

        filtered_df = df[df["date"] >= start_date].copy()

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
        
        df["delta"] = df.apply(
            lambda row: row["total_value"] if row["transaction_type"] == "buy" else -row["total_value"],
            axis = 1
        )
        df_grouped = df.groupby("date", as_index=False)["delta"].sum()
        df_grouped["total_portfolio_value"] = df_grouped["delta"].cumsum()

        filtered_df = df_grouped[df_grouped["date"] >= start_date].copy()

        fig_total_line = px.line(filtered_df, 
                        x='date', 
                        y='total_portfolio_value', 
                        markers=True)
        
        fig_total_line.update_traces(
            line=dict(color='#039be5', width=5),
            fill='tozeroy',
            fillcolor="rgba(3, 155, 229, 0.3)",
            hovertemplate="Date: %{x}<br>Total: %{y}<extra></extra>",
            hoverlabel=dict(font_family="Markazi Text", font_size=20)
        )
        
        fig_total_line.update_layout(
            legend={'font': {'size': 16}},
            xaxis_title=None, yaxis_title=None,
            title={'font': {'size': 30}, 'x': 0.5, 'xanchor': 'center'},
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

######################### Pie chart #############################################

    @callback(
        Output('pie_total_plot', 'figure'),
        Input("portfolio-table", "rowData")
    )
    def update_pie_chart(row_data):
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
                plot_bgcolor="#303655",
                paper_bgcolor="#303655"
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
            textfont=dict(color='white'),
            hovertemplate="<b>%{label}</b><br>Total: %{value}$<br>Percentage: %{percent}",
            hoverlabel=dict(font_family="Markazi Text", font_size=20)
        )
        
        fig_total_pie.update_layout(
            legend=dict(orientation='v', yanchor="top", font=dict(size=14, color="#f2f2f2")),
            plot_bgcolor="#303655",
            paper_bgcolor="#303655",
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
        Output("portfolio-table", "rowData", allow_duplicate=True),
        Output("name-input", "value"),
        Output("category-input", "value"),
        Output("price-input", "value"),
        Output("qty-input", "value"),
        Output("buy-date-input", "value"),
        Output('portfolio-history-table', 'rowData', allow_duplicate=True),
        Input("submit-item", "n_clicks"),
        State("name-input", "value"),
        State("category-input", "value"),
        State("price-input", "value"),
        State("qty-input", "value"),
        State("buy-date-input", "value"),
        prevent_initial_call=True
    )
    def add_item(n, name, category, price, qty, buy_date):
        if not n:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        if not all([name, category, price, qty, buy_date]):
            return False, no_update, name, category, price, qty, buy_date, no_update
        
        if (float(price) <= 0) or (float(qty) <= 0):
            return False, no_update, name, category, price, qty, buy_date, no_update
        
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
            
            df["add"] = "add"
            df["edit"] = "edit"
            df["delete"] = "delete"
            df["sell"] = "sell"

            history = pd.read_csv('data/portfolio_history.csv')

            return True, df.to_dict('records'), "", "", "", "", date.today().isoformat(), history.to_dict('records')
        
        except Exception as e:
            print(f"Error adding item {e}")
            return False, no_update, name, category, price, qty, buy_date, no_update

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
            f"Add more '{row_data.get('name', '')}'",
            date.today().isoformat(),
            row_id
        )

    @callback(
        Output("modal-add-more", "is_open", allow_duplicate=True),
        Output("portfolio-table", "rowData", allow_duplicate=True),
        Output('portfolio-history-table', 'rowData', allow_duplicate=True),
        Input("confirm-add-more", "n_clicks"),
        State("price-add-more", "value"),
        State("qty-add-more", "value"),
        State("buy-date-add-more", "value"),
        State("store-add-more-row", "data"),
        prevent_initial_call=True
    )
    def add_more_item(n_clicks, price, qty, buy_date, row_id):
        if not n_clicks or row_id is None:
            return no_update, no_update, no_update
        
        if not all([price, qty, buy_date]):
            return no_update, no_update, no_update
        
        price_float = float(price)
        qty_float = float(qty)
        
        if (price_float <= 0) or (qty_float <= 0):
            return no_update, no_update, no_update

        try:
            df = pd.read_csv("data/portfolio.csv")
            row_data = df[df['id'] == row_id]
            
            if row_data.empty:
                return no_update, no_update, no_update
            
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

            df["add"] = "add"
            df["edit"] = "edit"
            df["delete"] = "delete"
            df["sell"] = "sell"

            return False, df.to_dict('records'), history.to_dict('records')

        except Exception as e:
            print(f"Error adding more: {e}")
            return no_update, no_update, no_update

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
        Output("portfolio-table", "rowData", allow_duplicate=True),
        Output('portfolio-history-table', 'rowData', allow_duplicate=True),
        Input("confirm-edit", "n_clicks"),
        State("name-edit", "value"),
        State("category-edit", "value"),
        State("store-edit-row", "data"),
        prevent_initial_call=True
    )
    def confirm_edit(n_clicks, name, category, row_id):
        if not n_clicks or row_id is None:
            return no_update, no_update, no_update

        try:
            df = pd.read_csv("data/portfolio.csv")
            
            if df[df['id'] == row_id].empty:
                return no_update, no_update, no_update
            
            df.loc[df['id'] == row_id, 'name'] = name
            df.loc[df['id'] == row_id, 'category'] = category
            
            df.to_csv("data/portfolio.csv", index=False)

            history = pd.read_csv("data/portfolio_history.csv")
            history.loc[history['asset_id'] == row_id, 'name'] = name
            history.loc[history['asset_id'] == row_id, 'category'] = category
            history.to_csv("data/portfolio_history.csv", index=False)

            df["add"] = "add"
            df["edit"] = "edit"
            df["delete"] = "delete"
            df["sell"] = "sell"

            return False, df.to_dict('records'), history.to_dict('records')

        except Exception as e:
            print(f"Error editing item: {e}")
            return no_update, no_update, no_update

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
        Output("portfolio-table", "rowData", allow_duplicate=True),
        Output('portfolio-history-table', 'rowData', allow_duplicate=True),
        Input("confirm-delete", "n_clicks"),
        State("store-delete-row", "data"),
        prevent_initial_call=True
    )
    def confirm_delete(n_clicks, row_id):
        if not n_clicks or row_id is None:
            return no_update, no_update, no_update

        try:
            df = pd.read_csv("data/portfolio.csv")
            df = df[df['id'] != row_id]
            df.to_csv("data/portfolio.csv", index=False)
            
            history = pd.read_csv("data/portfolio_history.csv")
            history = history[history['asset_id'] != row_id]
            history.to_csv("data/portfolio_history.csv", index=False)
            
            df["add"] = "add"
            df["edit"] = "edit"
            df["delete"] = "delete"
            df["sell"] = "sell"
            
            return False, df.to_dict('records'), history.to_dict('records')
        
        except Exception as e:
            print(f"Error deleting item: {e}")
            return True, no_update, no_update

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
        Output("portfolio-table", "rowData", allow_duplicate=True),
        Output('portfolio-history-table', 'rowData', allow_duplicate=True),
        Input("confirm-sell", "n_clicks"),
        State("price-sell", "value"),
        State("quantity-sell", "value"),
        State("date-sell", "value"),
        State("store-sell-row", "data"),
        prevent_initial_call=True
    )

    def confirm_sell(n_clicks, price, qty, sell_date, row_id):
        if not n_clicks or row_id is None:
            return no_update, no_update, no_update
        
        if not all([price, qty, sell_date]):
            return no_update, no_update, no_update

        price = float(price)
        qty = float(qty)

        if (price < 0) or (qty < 0):
            return no_update, no_update, no_update

        try:
            df = pd.read_csv("data/portfolio.csv")
            row_data = df[df['id'] == row_id]

            if row_data.empty:
                return no_update, no_update, no_update
            
            row = row_data.iloc[0].to_dict()
            
            old_quantity = float(row["quantity"])
            old_price = float(row["buy_price"])

            if qty > old_quantity:
                return no_update, no_update, no_update
            
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

            if not df.empty:
                df["add"] = "add"
                df["edit"] = "edit"
                df["delete"] = "delete"
                df["sell"] = "sell"

            return False, df.to_dict('records'), history.to_dict('records')

        except Exception as e:
            print(f"Error {e}")
            return no_update, no_update, no_update
        
