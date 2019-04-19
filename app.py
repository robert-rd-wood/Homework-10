import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from datetime import datetime

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""    

    # Determine first data point in database
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()[0]

    # Determine most recent data point in database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    return (
        f"<br/>"
        f"<h1 align=center>Welcome to the Surf's Up Flask API</h1><br/>"
        f"<h3>Available Routes:</h3>"
        f"<b><a href=/api/v1.0/precipitation>/api/v1.0/precipitation</a></b><br/>"
        f"Converts the query results to a Dictionary using date as the key and prcp as the value.<br/>"
        f"Returns the JSON representation of your dictionary.<br/>"
        f"<br/>"
        f"<b><a href=/api/v1.0/stations>/api/v1.0/stations<a></b><br/>"
        f"Returns a JSON list of stations from the dataset.<br/>"
        f"<br/>"
        f"<b><a href=/api/v1.0/tobs>/api/v1.0/tobs<a></b><br/>"
        f"Query for the dates and temperature observations from a year from the last data point.<br/>"
        f"Returns a JSON list of Temperature Observations (tobs) for the previous year.<br/>"
        f"<br/>"
        f"<b>/api/v1.0/&lt;start&gt;</b><br/>"
        f"Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.<br/>"
        f"Calculates TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.<br/>"
        f"<i>Note: Available date range is {first_date} to {last_date}.</i><br/>"
        f"<br/>"
        f"<b>/api/v1.0/&lt;start&gt;/&lt;end&gt;</b><br/>"
        f"Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.<br/>"
        f"Calculates the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.<br/>"
        f"<i>Note: Available date range is {first_date} to {last_date}.</i>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value."""
    """Returns the JSON representation of your dictionary."""
    
    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create dictionary of results
    all_prcp = dict(results)
 
    # Return jsonified dictionary
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    # Query all passengers
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return jsonified dictionary
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point."""
    """Returns a JSON list of Temperature Observations (tobs) for the previous year."""

    # Determine most recent data point in database
    result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = datetime.strptime(result,'%Y-%m-%d')

    # Calculate date one year prior
    year_ago = query_date - dt.timedelta(days=365)

    # Query temperature data
    results = session.query(Measurement.date, Measurement.tobs).\
                            filter(Measurement.date >= year_ago).\
                            filter(Measurement.date <= query_date).all()

    # Create dictionary of results
    all_tobs = dict(results)

    # Return jsonified dictionary
    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    """Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""
    """Calculates TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""

    """Begin Error Checking"""

    # Ensure the date passed is prior to the last date for which data is available
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # If not, return an error message
    if start > latest_date:
        return(f"<b>Error:</b> No data available in the specified timeframe.  Please enter a date less than {latest_date}.")

    # If the start date passed is prior to the first date with available data,
    # reassign start date to the first date with data available (for clarification when printing results)
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()[0]
    if start < first_date:
        start = first_date

    """End Error Checking"""

    # Query temperature data
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()

    # Convert list of tuples into normal list
    summary = list(np.ravel(results))
    
    # Return formatted results
    return(f"<h3>Temperature results for date range starting {start}:</h3>"
        f"Minimum: {'{:.2f}'.format(summary[0])} F<br/>"
        f"Average: {'{:.2f}'.format(summary[1])} F<br/>"
        f"Maximum: {'{:.2f}'.format(summary[2])} F"
        )


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    """Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range."""
    """Calculates the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

    """Begin Error Checking"""

    # Ensure the start date passed is prior to the last date for which data is available
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # If not, return an error message
    if start > latest_date:
        return(f"<b>Error:</b> No data available in the specified timeframe.  Please enter a start date less than {latest_date}.")

    # Ensure the end date passed is more recent than the first date for which data is available
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()[0]
    # If not, return an error message
    if end < first_date:
        return(f"<b>Error:</b> No data available in the specified timeframe.  Please enter an end date greater than {first_date}.")

    # Ensure the start date passed is prior to the end date passed
    # If not, return an error message
    if start > end:
        return(f"<b>Error:</b> Please ensure the start date entered is prior to the end date.")

    # If the start date passed is prior to the first date with available data,
    # reassign start date to the first date with data available (for clarification when printing results)
    if start < first_date:
        start = first_date
    
    # If the end date passed is after the last date with available data,
    # reassign end date to the last date with data available (for clarification when printing results)
    if end > latest_date:
        end = latest_date

    """End Error Checking"""

    # Query temperature data
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()

    # Convert list of tuples into normal list
    summary = list(np.ravel(results))

    # Return formatted results
    return(f"<h3>Temperature results for date range {start} to {end}:</h3>"
        f"Minimum: {'{:.2f}'.format(summary[0])} F<br/>"
        f"Average: {'{:.2f}'.format(summary[1])} F<br/>"
        f"Maximum: {'{:.2f}'.format(summary[2])} F"
        )


if __name__ == '__main__':
    app.run(debug=True)
