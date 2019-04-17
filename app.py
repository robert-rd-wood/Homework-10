import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Converts the query results to a Dictionary using date as the key and prcp as the value.<br/>"
        f"Returns the JSON representation of your dictionary.<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"Returns a JSON list of stations from the dataset.<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Query for the dates and temperature observations from a year from the last data point.<br/>"
        f"Returns a JSON list of Temperature Observations (tobs) for the previous year.<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.<br/>"
        f"Calculates TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.<br/>"
        f"Calculates the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value."""
    """Returns the JSON representation of your dictionary."""
    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()
 
    # Create a dictionary from the row data and append to a list of all_prcp
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)
    
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all passengers
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point."""
    """Returns a JSON list of Temperature Observations (tobs) for the previous year."""
    # Determine most recent data point in database
    query_date = dt.date(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    # Calculate date one year prior
    year_ago = query_date - dt.timedelta(days=365)

    # Query temperature data
    results = session.query(Measurement.date, Measurement.tobs).\
                            filter(Measurement.date >= year_ago).\
                            filter(Measurement.date <= query_date).all()

    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start():
    """Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""
    """Calculates TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""


@app.route("/api/v1.0/<start>/<end>")
def start_end():
    """Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range."""
    """Calculates the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""


if __name__ == '__main__':
    app.run(debug=True)
