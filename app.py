from dash import Dash
import dash_bootstrap_components as dbc
from components.layout import serve_layout
from components.callbacks import register_callbacks

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,         
        'https://unpkg.com/ag-grid-community/styles/ag-grid.css',
        'https://unpkg.com/ag-grid-community/styles/ag-theme-alpine.css']
    )

app.title = 'Custom portfolio dashboard'

app.layout = serve_layout()

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug = True)