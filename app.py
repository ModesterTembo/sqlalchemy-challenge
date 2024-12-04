from flask import Flask, jsonify
import datetime as dt
import pandas as pd
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_data = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_data - dt.timedelta(days=365)

    # Query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Query to retrieve all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Identify the most active station
    most_active_station_id = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year from the last date in dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_data = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_data - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for the most active station
    temperature_data = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert list of tuples into normal list
    temperature_list = list(np.ravel(temperature_data))

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start=None, end=None):
    # Define the selection criteria for the query
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end:
        # Query the minimum, average, and maximum temperature for the specified start and end date range
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        # Query the minimum, average, and maximum temperature for the specified start date
        results = session.query(*sel).filter(Measurement.date >= start).all()

    # Convert list of tuples into normal list
    temp_list = list(np.ravel(results))

    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)
