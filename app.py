from dash import Dash
from components.layout import serve_layout
from components.callbacks import register_callbacks

app = Dash(__name__)

app.title = 'Custom portfolio dashboard'

app.layout = serve_layout()

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug = True)