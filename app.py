from dash import Dash
from components.layout import server_layout
# from components.callbacks import register_callbacks

app = Dash(__name__)

app.title = 'Custom portfolio dashboard'

app.layout = server_layout()

if __name__ == "__main__":
    app.run()