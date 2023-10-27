from dash import html, dcc, Dash
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine

# Connect to the Sakila database
engine = create_engine('mysql://root:aswin2004@localhost/sakila')

# Create the Dash app
app = Dash(__name__)

# Populate categories dynamically
categories = pd.read_sql("SELECT category_id, name FROM category", engine)
category_options = [{'label': cat['name'], 'value': cat['category_id']} for _, cat in categories.iterrows()]

# Define the layout of the app
app.layout = html.Div([
    html.H1("Top 5 Films by Revenue"),
    
    dcc.Dropdown(
        id='category-dropdown',
        options=category_options,
        value=category_options[0]['value']  # Default selected option
    ),
    
    dcc.Graph(id='bar-chart'),
])

@app.callback(
    Output('bar-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_bar_chart(selected_category):
    query = f"""
    SELECT title, SUM(payment.amount) AS total_revenue
    FROM film
    JOIN film_category ON film.film_id = film_category.film_id
    JOIN inventory ON film.film_id = inventory.film_id
    JOIN rental ON inventory.inventory_id = rental.inventory_id
    JOIN payment ON rental.rental_id = payment.rental_id
    WHERE film_category.category_id = {selected_category}
    GROUP BY film.title
    ORDER BY total_revenue DESC
    LIMIT 5;
    """
    rental_data = pd.read_sql(query, engine)

    fig = {
        'data': [
            {
                'x': rental_data['title'],
                'y': rental_data['total_revenue'],  # Note the column name change
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Top 5 Films by Revenue for Category {selected_category}',
            'xaxis': {'title': 'Film Title'},
            'yaxis': {'title': 'Revenue'}
        }
    }

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
