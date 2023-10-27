import influxdb_client
from sqlalchemy import create_engine
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import os
# InfluxDB settings
token = "AGvgSBuFfR5j2eCq9kCfq4QBwiqiMBhPnd4fLz2VrEzzZldHaTX4t9Tj1UpGIsiUOgt2zhTwPGcxNm7ZcFtugA=="
org = "IEU"
url = "http://localhost:8086"
bucket = "aswin_bucket"


# Initialize InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Initialize SQLAlchemy engine for MySQL
engine = create_engine('mysql://root:hoqhor-fyjMim-dughe5@localhost/sakila')

# Your SQL query
query = """
SELECT
        f.title AS movie_title,
        SUM(p.amount) AS revenue
    FROM
        film f
    JOIN
        inventory i ON f.film_id = i.film_id
    JOIN
        rental r ON i.inventory_id = r.inventory_id
    JOIN
        payment p ON r.rental_id = p.rental_id
    JOIN
        film_category fc ON f.film_id = fc.film_id
    JOIN
        category cat ON fc.category_id = cat.category_id
    WHERE
        cat.name = 'Family'
    GROUP BY
        f.title
    ORDER BY
        revenue DESC
    LIMIT 5;
"""

data = pd.read_sql(query, engine)

points = []
# Create a point for each data row
for row in data.itertuples(index=False):
    point = Point("movie_revenue").tag("movie_title", row.movie_title).field("revenue", row.revenue)
    points.append(point)

# Write points to InfluxDB
write_api.write(bucket=bucket, record=points, write_precision=WritePrecision.NS)

# Close the client
client.close()