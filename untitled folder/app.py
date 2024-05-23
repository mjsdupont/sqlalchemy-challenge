# Import the dependencies.
import numpy as np
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///sqlalchemy-challenge\SurfsUp\Resources\hawaii.sqlite") 

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
def home():
    """List all available api routes."""
    return (
        f"<b>Available Routes: </b> <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"  
        f"<b>Note</b>: for /api/v1.0/<start><br/> ensure the 'start date' uses the following format: YYYY-mm-dd <br/>"
        f"<b>Note</b>: for /api/v1.0/<start>/<end><br/> use the following format to assess the 'start and end dates': YYYY-mm-dd/YYYY-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitations():
    # Query precipitation analysis from the last 12 months
    precipitation_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= '2016-08-23').filter(measurement.date <= '2017-08-23').all()

    session.close()

precip_12 = []
    for date, prcp in precipitation_data:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        precip_12.append(measurement_dict)

    return jsonify(precip_12)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(station.station).all()
    session.close()
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperatures():
    """Return a JSON list of temperatures, and dates from the dataset."""
    # Query all stations
    year_temp = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >'2016-08-23').filter(measurement.date < '2017-08-23').filter(measurement.station == "USC00519281").\
    group_by(measurement.tobs, measurement.date).\
    order_by(measurement.date).all()
    session.close()

popular_station = []
    for date, temperatures in year_temp:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["tobs"] = temperatures
        popular_station.append(measurement_dict)
    return jsonify(popular_station)

@app.route("/api/v1.0/<start>")
# Define function, set "start" date entered by user as parameter for start_date decorator 
def start_date(start):
    session = Session(engine) 

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # Create query for minimum, average, and max tobs where query date is greater than or equal to the date the user submits in URL
    start_date_tobs_results = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    
    session.close() 

start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)

@app.route("/api/v1.0/<start>/<end>")

def Start_end_date(start, end):
    session = Session(engine)

    """Return a list of min, avg and max tobs between start and end dates entered"""

start_end_date_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict) 
    

    return jsonify(start_end_tobs_date_values)

if __name__ == '__main__':
    app.run(debug=True) 
