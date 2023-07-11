# Dependencies
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Create engine for Hawaii climate database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app
app = Flask(__name__)

# Define a function to get the date one year from the most recent date
def get_previous_year_date():
    # Create a session
    session = Session(engine)

    # Get the most recent date in the Measurement dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year from the last date
    previous_year_date = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Close the session
    session.close()

    # Return the date
    return previous_year_date

# Define the homepage route
@app.route("/")
def homepage():
    return """ <h2> Welcome to the Hawaii Climate API! </h2>
    <ul>
    <li><a href="/api/v1.0/precipitation">Precipitation</a>: <strong>/api/v1.0/precipitation</strong></li>
    <li><a href="/api/v1.0/stations">Stations</a>: <strong>/api/v1.0/stations</strong></li>
    <li><a href="/api/v1.0/tobs">TOBS</a>: <strong>/api/v1.0/tobs</strong></li>
    <li>To retrieve min, avg, and max temperatures for a specific date, use <strong>/api/v1.0/&lt;start&gt;</strong> (replace start date in yyyy-mm-dd format)</li>
    <li>To retrieve min, avg, and max temperatures for a specific date range, use <strong>/api/v1.0/&lt;start&gt;/&lt;end&gt;</strong> (replace start and end dates in yyyy-mm-dd format)</li>
    </ul>
    """

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def get_precipitation():
    # Create a session
    session = Session(engine)

    # Query precipitation data from the last 12 months
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= get_previous_year_date()).all()

    # Close the session
    session.close()

    # Create a list of dictionaries for precipitation data
    precipitation_list = []
    for date, prcp in prcp_data:
        precipitation_dict = {"date": date, "prcp": prcp}
        precipitation_list.append(precipitation_dict)

    # Return the jsonified precipitation data for the previous 12 months
    return jsonify(precipitation_list)

# Define the stations route
@app.route("/api/v1.0/stations")
def get_stations():
    # Create a session
    session = Session(engine)

    # Query station data from the Station table
    station_data = session.query(Station.station).all()

    # Close the session
    session.close()

    # Convert the list of tuples into a normal list
    station_list = list(np.ravel(station_data))

    # Return the jsonified station data
    return jsonify(station_list)

# Define the TOBS route
@app.route("/api/v1.0/tobs")
def get_tobs():
    # Create a session
    session = Session(engine)

    # Query TOBS data from the last 12 months for USC00519281 station
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= get_previous_year_date()).all()

    # Close the session
    session.close()

    # Create a list of dictionaries for TOBS data
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {"date": date, "tobs": tobs}
        tobs_list.append(tobs_dict)

    # Return the jsonified TOBS data for the previous 12 months
    return jsonify(tobs_list)

# Define the temperature route for a specific start date or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def get_temperature(start=None, end=None):
    # Create a session
    session = Session(engine)

    # Define a list to query (minimum, average, and maximum temperature)
    temperature_query = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Check if there is an end date, then perform the task accordingly
    if end is None:
        # Query the data from the start date to the most recent date
        start_data = session.query(*temperature_query).\
            filter(Measurement.date >= start).all()
        # Convert the list of tuples into a normal list
        start_list = list(np.ravel(start_data))

        # Return the jsonified minimum, average, and maximum temperatures for a specific start date
        return jsonify(start_list)
    else:
        # Query the data from the start date to the end date
        start_end_data = session.query(*temperature_query).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        # Convert the list of tuples into a normal list
        start_end_list = list(np.ravel(start_end_data))

        # Return the jsonified minimum, average, and maximum temperatures for a specific start-end date range
        return jsonify(start_end_list)

    # Close the session
    session.close()

# Define the main branch
if __name__ == "__main__":
    app.run(debug=True)