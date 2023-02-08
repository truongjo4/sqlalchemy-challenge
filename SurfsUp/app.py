import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#####################################
# Database setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#####################################
# Flask setup

app = Flask(__name__)

# Flask routes

@app.route("/")
def welcome():
    "List of all available api routes."
    return (
        f"Available Static Routes:<br/>"
        f"/api/v1.0/precipitation => Returns recorded date and precipitation values. <br/>"
        f"/api/v1.0/stations => Returns list of station names (ID) <br/>"
        f"/api/v1.0/tobs => Returns recorded date and temperature values. <br/><br/>"
        f"Available dynamic Routes - You can specify start and end dates (format = YYYY-MM-DD). <br/>"
        f"This will return the minimum, maximum, and average temperature recorded between the dates provided. <br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/><br/>"
        f"e.g. /api/v1.0/2015 -> Returns data from 2015 onwards.  <br/>"
        f"e.g. /api/v1.0/2012-03-01/2016 -> Returns data from March of 2012 to 2016.  <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Search past year -> save date and precipitation values in dictionary -> return as json
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= prev_year).all()

    session.close()

    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Only return station names from station table
    station_names = session.query(Station.station).all()

    session.close()

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")   
def tobs():
    session = Session(engine)

    # Search past year -> save temp from most active station -> return as json
    prev_year = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    temperature = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date >= prev_year)\
    .filter(Measurement.station == "USC00519281")\
    .all() 

    session.close()

    temp = {date: temp for date, temp in temperature} 
    return jsonify(temp)        

@app.route("/api/v1.0/<start_date>")
def start_date_only(start_date):
    session = Session(engine)

    # Specified start date will return json of min, max and avg temperature
    info = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
    .filter(Measurement.date >= start_date)\
    .all()

    session.close()

    start_info = {"min":info[0][0], "max":info[0][1], "avg":info[0][2]}

    return jsonify(start_info)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date, end_date):
    session = Session(engine)

    # specified start + end date will return json of min, max and avg temperature
    info = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
    .filter(Measurement.date >= start_date)\
    .filter(Measurement.date <= end_date)\
    .all()

    session.close()
    
    start_end_info = {"min":info[0][0], "max":info[0][1], "avg":info[0][2]}

    return jsonify(start_end_info)

if __name__ == '__main__':
    app.run(debug=True)