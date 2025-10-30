from dash import html, dcc, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import dash_ag_grid as dag
from datetime import date

###################################### Modal add_item_button &  ######################################

alert_add_item = html.Div(
    [
        html.Hr(),
        dbc.Alert(
            "Item added successfully",
            id="alert-add-item",
            is_open=False,
            duration=3000,
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
                    dbc.Button("Close", id="close-add-item", color="danger", n_clicks=0),
            ]),
            ],
            id="modal-add-button",
            is_open=False,
            className="custom_model_css"
        ),
    ], className="add_item_container"
)

###############################   Header    ###################################################

header = html.Div([
    html.Div(html.H1("DataVault"), className="logo_header"),
    html.Div(
        children= [
            html.Div('feauture1', className='header_icon'),
            html.Div('feauture2', className='header_icon'),
            html.Div(add_item_button, className='header_icon'),
        ], className="header_icons_container"
    )
], className="header_container"
)

##################################### Basic Data ############################################


df = pd.read_csv('data/portfolio.csv')

df['total_value'] = df['buy_price'] * df['quantity']
df_total = df.groupby('buy_date')['total_value'].sum().reset_index()
df_total = df.sort_values('buy_date')
df_total['cumulative_total'] = df_total['total_value'].cumsum()

###############################   Pie graph    ###################################################

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
    paper_bgcolor="#303655",
    showlegend=False
    )
######################################## Info panel ###############################################

info_panel = html.Div(
            className='info_panel',
            children=[
                html.Div('Total Value: 1234$', className='info_box'),
                html.Div('Most expensive item: 1554$', className='info_box'),
                html.Div('The cheapest item: 3421$', className='info_box'),
                html.Div('Average item price: 12323414$', className='info_box'),
                html.Div('First bought: Rolex 2012 gold', className='info_box'),
                html.Div('Last bought: buggati 2021', className='info_box'),
                html.Div('Number of Assets: 4331', className='info_box'),
            ],
        )

######################################## Time buttons ###############################################

time_buttons = html.Div([
    html.Button("1D", id="btn-1d", n_clicks=0, className="time-btn"),
    html.Button("1W", id="btn-1w", n_clicks=0, className="time-btn"),
    html.Button("1M", id="btn-1m", n_clicks=0, className="time-btn"),
    html.Button("6M", id="btn-6m", n_clicks=0, className="time-btn"),
    html.Button("1Y", id="btn-1y", n_clicks=0, className="time-btn"),
    html.Button("ALL", id="btn-all", n_clicks=0, className="time-btn active")
], className="time-filter")

########################################## Table #############################################

df["edit"] = "edit"
df["delete"] = "delete"
df["sell"] = "sell"

table = html.Div(
    dag.AgGrid(
        id='portfolio-table',
        rowData=df.to_dict('records'),
        columnDefs=[
            {"field": "name", "headerName": "Name", "resizable": False,},
            {"field": "category", "headerName": "Category", "resizable": False,},
            {"field": "buy_price", "headerName": "Buy Price", "resizable": False,"valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
            {"field": "quantity", "headerName": "Quantity", "resizable": False,},
            {"field": "buy_date", "headerName": "Buy Date", "resizable": False, },
            {"field": "total_value", "headerName": "Total Value", "resizable": False,  "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
            {"field": "edit", "headerName": "", "filter": False, "sortable": False, "resizable": False, "maxWidth": 80,},
            {"field": "delete", "headerName": "", "filter": False, "sortable": False, "resizable": False, "maxWidth": 80,},
            {"field": "sell", "headerName": "", "filter": False, "sortable": False, "resizable": False, "maxWidth": 80, },
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
            "suppressHorizontalScroll": True
        },
        style={"width": "100%", "height": "100%"},
        className='ag-theme-alpine'
    ),
    className='portfolio_table_css'
)

####################################### delete button ##########################################

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

#######################################  edit  ######################################

store_edit_row = dcc.Store(id="store-edit-row", data=None)

modal_edit = dbc.Modal(
            [
                dbc.ModalHeader("Edit item"),
                dbc.ModalBody([
                    dbc.Input(id="name-edit", placeholder="Name", type="text"),
                    dbc.Input(id="category-edit", placeholder="Category", type="text", className="mt-2"),
                    dbc.Input(id="price-edit", placeholder="Buy price", type="number", className="mt-2"),
                    dbc.Input(id="qty-edit", placeholder="Quantity", type="number", className="mt-2"),
                    dbc.Input(id="buy-date-edit", placeholder="Buy date (yyyy-mm-d)", type="date", className="mt-2"),
                ]),
                store_edit_row,
                dbc.ModalFooter([
                    dbc.Button("Confirm", id="confirm-edit", color="success"),
            ]),
            ],
            id="modal-edit",
            is_open=False,
            className=""
        )
##################################### Serve layout ############################################

def serve_layout():
    return html.Div([

        header,

        html.H2('Custom portfolio dashboard', className = 'header'),

        info_panel,

        html.Div(time_buttons, className='time_buttons_container'),

        html.Div([
            html.Div([
                dcc.Graph(id = 'line_total_plot', config={'displayModeBar':False})
                ], className='graph_container_line'),
            html.Div([dcc.Graph(id = 'pie_total_plot', figure = fig_total_pie, config={'displayModeBar':False})], className= 'graph_container_pie')],
            className='graph_containers_total'),

        html.Div([
            html.H2('Portfolio details', className='portfolio_details_h2'),

            html.Div(table, className = 'table_style_container'),
            modal_delete,
            modal_edit,
            ],
            className='container_table_general'),
    ])