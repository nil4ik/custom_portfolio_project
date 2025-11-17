from dash import html, dcc, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import dash_ag_grid as dag
from datetime import date
import uuid

###################################### Navigation tabs ############################################

navigation_tabs = html.Div(html.Div([
    dbc.Tabs(
        id="main-tabs",
        active_tab="dashboard",
        children=[
            dbc.Tab(label="Dashboard", tab_id="dashboard", className="custom-tab"),
            dbc.Tab(label="Portfolio", tab_id="portfolio", className="custom-tab"),
            dbc.Tab(label="Transactions", tab_id="transactions", className="custom-tab"),
        ],
        className="custom-tabs-nav"
    ),
], className="tabs-container"), className="tabs-main-container")

###################################### Modal add_item_button  ######################################

alert_add_item = html.Div(
    [
        html.Hr(),
        dbc.Alert(
            "Item added successfully",
            id="alert-add-item",
            is_open=False,
            duration=2000,
            className="alert_css"
        ),
    ], className="alert_container"
)

add_item_button = html.Div(
    [
        dbc.Button("Add item", id="open-add-item", n_clicks=0, className="add_item_button"),
        dbc.Modal(
            [
                dbc.ModalHeader("Add new item to portfolio"),
                dbc.ModalBody([
                    dbc.Input(id="name-input", placeholder="Name", type="text"),
                    dbc.Input(id="category-input", placeholder="Category", type="text", className="mt-2"),
                    dbc.Input(id="price-input", placeholder="Buy price", type="number", className="mt-2"),
                    dbc.Input(id="qty-input", placeholder="Quantity", type="number", className="mt-2"),
                    dbc.Input(id="buy-date-input", placeholder="Buy date (yyyy-mm-d)", type="date", className="mt-2", value=date.today().isoformat()),
                    alert_add_item
                ]),
                dbc.ModalFooter([
                    dbc.Button("Add", id="submit-item", color="success"),
            ]),
            ],
            id="modal-add-button",
            is_open=False,
            className="custom_model_css"
        ),
    ], className="add_item_container"
)

###############################   Header   ###################################################

header = html.Div(html.Div([
    html.Div(html.H1("DataVault"), className="logo_header"),
    html.Div(
        children= [
            html.Div(add_item_button, className='header_icon'),
        ], className="header_icons_container"
    )
], className="header_container"
), className="header_main_container")

######################################## Info panel ###############################################

info_panel = html.Div(
            className='info_panel',
            children=[
                html.Div(id='total-value-box', className='info_box'),
                html.Div(id='number-of-assets-box', className='info_box'),
                html.Div(id='most-expensive-box', className='info_box'),
                html.Div(id='average-price-box', className='info_box'),
                html.Div(id='popular-category-box', className='info_box'),
                html.Div(id='profit-loss-box', className='info_box'),
            ],
        )

######################################## Time buttons ###############################################

time_buttons = html.Div([
    html.Button("1d", id="btn-1d", n_clicks=0, className="time-btn"),
    html.Button("1w", id="btn-1w", n_clicks=0, className="time-btn"),
    html.Button("1m", id="btn-1m", n_clicks=0, className="time-btn"),
    html.Button("6m", id="btn-6m", n_clicks=0, className="time-btn"),
    html.Button("1y", id="btn-1y", n_clicks=0, className="time-btn"),
    html.Button("all", id="btn-all", n_clicks=0, className="time-btn active")
], className="time-filter")

########################################## Table #############################################

table = html.Div(
    dag.AgGrid(
        id='portfolio-table',
        rowData= [],
        columnDefs=[
            {"field": "id", "hide": True},
            {"field": "name", "headerName": "Name", "resizable": False,},
            {"field": "category", "headerName": "Category", "resizable": False,},
            {"field": "buy_price", "headerName": "Buy Price", "resizable": False,"valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
            {"field": "quantity", "headerName": "Quantity", "resizable": False,},
            {"field": "buy_date", "headerName": "Buy Date", "resizable": False, },
            {"field": "total_value", "headerName": "Total Value", "resizable": False,  "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
            {"field": "add", "headerName": "", "filter": False, "sortable": False, "resizable": False, "width": 10, "flex": 0},
            {"field": "edit", "headerName": "", "filter": False, "sortable": False, "resizable": False, "width": 10, "flex": 0},
            {"field": "delete", "headerName": "", "filter": False, "sortable": False, "resizable": False, "width": 10, "flex": 0},
            {"field": "sell", "headerName": "", "filter": False, "sortable": False, "resizable": False, "width": 10, "flex": 0},
        ],
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "flex": 1,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20,
            "domLayout": "autoHeight",
            "suppressHorizontalScroll": True,
            "getRowId": {"function": "params.data.id"}
        },
        style={"width": "100%", "height": "100%"},
        className='ag-theme-alpine'
    ),
    className='portfolio_table_css'
)

###################################### Modal add more button ########################################


store_add_more_row = dcc.Store(id="store-add-more-row", data=None)

modal_add_more = dbc.Modal(
            [
                dbc.ModalHeader(id="modal-add-more-header"),
                dbc.ModalBody([
                    dbc.Input(id="price-add-more", placeholder="Buy price", type="number", className="mt-2"),
                    dbc.Input(id="qty-add-more", placeholder="Quantity", type="number", className="mt-2"),
                    dbc.Input(id="buy-date-add-more", placeholder="Buy date (yyyy-mm-d)", type="date", className="mt-2"),
                ]),
                store_add_more_row,
                dbc.ModalFooter([
                    dbc.Button("Confirm", id="confirm-add-more", color="success"),
            ]),
            ],
            id="modal-add-more",
            is_open=False,
            className = "custom_model_css",
        )

####################################### Modal delete button ##########################################

store_delete_row = dcc.Store(id="store-delete-row", data=None)

modal_delete = dbc.Modal(
    [
        dbc.ModalHeader("Confirm Deletion"),
        dbc.ModalBody(id="modal-delete-body"),
        store_delete_row,
        dbc.ModalFooter([
            dbc.Button("Confirm", id="confirm-delete", color="success"),
        ])
    ],
    className = "custom_model_css",
    id="delete-modal",
    is_open=False,
)

####################################### Modal edit button ######################################

store_edit_row = dcc.Store(id="store-edit-row", data=None)

modal_edit = dbc.Modal(
            [
                dbc.ModalHeader("Edit item"),
                dbc.ModalBody([
                    dbc.Input(id="name-edit", placeholder="Name", type="text"),
                    dbc.Input(id="category-edit", placeholder="Category", type="text", className="mt-2"),
                ]),
                store_edit_row,
                dbc.ModalFooter([
                    dbc.Button("Confirm", id="confirm-edit", color="success"),
            ]),
            ],
            id="modal-edit",
            is_open=False,
            className = "custom_model_css",
        )

####################################### Modal sell button ######################################


store_sell_row = dcc.Store(id="store-sell-row", data=None)

modal_sell = dbc.Modal(
            [
                dbc.ModalHeader(id="modal-sell-header"),
                dbc.ModalBody([
                    dbc.Input(id="price-sell", placeholder="Sell price", type="text", className="mt-2"),
                    dbc.Input(id="quantity-sell", placeholder="Quantity", type="text", className="mt-2"),
                    dbc.Input(id="date-sell", placeholder="Buy date (yyyy-mm-d)", type="date", className="mt-2"),

                ]),
                store_sell_row,
                dbc.ModalFooter([
                    dbc.Button("Confirm", id="confirm-sell", color="success"),
            ]),
            ],
            id="modal-sell",
            is_open=False,
            className = "custom_model_css",
        )

################################# history transaction ##############################

history = html.Div(
        dag.AgGrid(
        id='portfolio-history-table',
        rowData= [],
        columnDefs=[
            {"field": "transaction_id", "hide": True},
            {"field": "name", "headerName": "Name", "resizable": False,},
            {"field": "transaction_type", "headerName": "Type", "resizable": False, "cellStyle": {"function": """
             params.value === 'buy' ? {'color': 'green'} : {'color': 'red'} """}},
            {"field": "price", "headerName": "Price", "resizable": False,"valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
            {"field": "quantity", "headerName": "Quantity", "resizable": False,},
            {"field": "total_value", "headerName": "Total value", "resizable": False,"valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
            {"field": "date", "headerName": "Date", "resizable": False, "sort": "desc"},
            {"field": "profit_loss", "headerName": "Profit/Loss", "resizable": False, 
             "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}, 
             "cellStyle": {"function": """
             params.value > 0 ? {'color': 'green', 'fontWeight': 'bold'} : 
             params.value < 0 ? {'color': 'red', 'fontWeight': 'bold'} : {}"""}}
        ],
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "flex": 1,
        },
        dashGridOptions={
            "pagination": False,
            "domLayout": "normal",
            "suppressHorizontalScroll": True,
            "getRowId": {"function": "params.data.transaction_id"}
        },
        style={"width": "100%", "height": "650px"},
        className='ag-theme-alpine'
    ),
    className='portfolio_history_table_css'
)

####################################### footer ######################################

footer = html.Footer(
    [
        html.Span("© 2025 DataVault  Built by Daniils Nils Gosperskis"),
        html.Br(),
        html.A("nil4ik", href="https://github.com/nil4ik", target="_blank", className="footer-link"),
        html.Span(" | "),
        html.A("GitHub Repo", href="https://github.com/nil4ik/custom_portfolio_dash", target="_blank", className="footer-link"),
    ],
    className="footer_container"
)

#################################### Content functions ######################################

def dashboard_content():
    return html.Div([        
        info_panel,
        
        html.Div([
            html.Div([
                html.Div(time_buttons, className='time_buttons_container'),
                dcc.Graph(id='line_total_plot', config={'displayModeBar': False})
            ], className='graph_container_line', style={'backgroundColor': 'transparent'}),
            html.Div([
                dcc.Graph(id='pie_total_plot', config={'displayModeBar': False})
            ], className='graph_container_pie', style={'backgroundColor': 'transparent'})
        ], className='graph_containers_total'),
    ])

def portfolio_content():
    return html.Div([
        html.Div([
            html.Div(table, className='table_style_container'),
            modal_add_more,
            modal_delete,
            modal_edit,
            modal_sell,
        ], className='container_table_general'),
    ])

def transactions_content():
    return html.Div([
        html.Div(history, className='history_style_container')
    ])

##################################### Serve layout ############################################

def serve_layout():
    return html.Div([
        html.Div([
            dcc.Store(id='data-refresh-trigger', data=0),
            header,
            navigation_tabs,
            html.Div(id="page-content"),
        ], className='main-content'),
        footer,
    ], className='app-container')