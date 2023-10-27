import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine

# Connect to the Sakila database
engine = create_engine('mysql://root:@localhost/sakila')

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Sakila Rental Data Over Time"),
    
    # Dropdown to select a category
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': 'Category 1', 'value': 1},
            {'label': 'Category 2', 'value': 2}
        ], 
        value=1
    ),
    
    # Line chart to display data over time
    dcc.Graph(id='line-chart'),
    dcc.Graph(id='plot-chart'),
    dcc.Graph(id='part-chart')
])

@app.callback(
    Output('line-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_line_chart(selected_category):
    query = """
        SELECT DISTINCT c.first_name, c.last_name
        FROM customer c
        JOIN rental r ON c.customer_id = r.customer_id
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film f ON i.film_id = f.film_id
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category cat ON fc.category_id = cat.category_id
        WHERE cat.name = 'Family'
        """
    rental_data = pd.read_sql(query, engine)
    fig = {
        'data': [
            {
                'x': rental_data.iloc[:, 0],
                'y': rental_data.iloc[:, 1],
                'type': 'bar',
                'marker': {'color': 'green'}
            }
        ],
        'layout': {
            'title': f'Data for Exercise {selected_category}',
            'xaxis': {'title': 'First Name'},
            'yaxis': {'title': 'Last Name'}
        }
    }
    return fig

@app.callback(
    Output('plot-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_plot_chart(selected_category):
    query = """
        SELECT f.title, SUM(p.amount) as total_revenue
        FROM film f
        JOIN inventory i ON f.film_id = i.film_id
        JOIN rental r ON i.inventory_id = r.inventory_id
        JOIN payment p ON r.rental_id = p.rental_id
        GROUP BY f.title
        ORDER BY total_revenue DESC
        LIMIT 5
        """
    rental_data = pd.read_sql(query, engine)
    fig = {
        'data': [
            {
                'x': rental_data['title'],
                'y': rental_data['total_revenue'],
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Data for Exercise {selected_category}',
            'xaxis': {'title': 'Film Title'},
            'yaxis': {'title': 'Total Revenue'}
        }
    }
    return fig

@app.callback(
    Output('part-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_plot_chart3(selected_category):
    query = """
        SELECT c.first_name as first_name, c.last_name, SUM(p.amount) as total_payments
        FROM customer c
        JOIN payment p ON c.customer_id = p.customer_id
        GROUP BY c.customer_id
        ORDER BY total_payments DESC
        """
    total_payments = pd.read_sql(query, engine)
    fig = {
        'data': [
            {
                'x': total_payments['first_name'],
                'y': total_payments['total_payments'],
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Data for Exercise {selected_category}',
            'xaxis': {'title': 'Customer Name'},
            'yaxis': {'title': 'Total Payments'}
        }
    }
    return fig

if __name__ == "__main__":
    app.run_server(debug=True,port=8051)
