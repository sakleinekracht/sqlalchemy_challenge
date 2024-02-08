# Import the dependencies.

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
engine = create_engine("sqlite:////Users/sarakleine-kracht/Desktop/sqlalchemy_challenge/SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Welcome!"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation data for the last year"""

    #query to retrieve the precipitation for the last year
    year_of_data = dt.date(2017,8,23)-dt.timedelta(days=365)
    latest_date = dt.date(year_of_data.year, year_of_data.month, year_of_data.day)
    precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= latest_date).order_by(measurement.date.desc()).all()

    session.close()

      # Create a dictionary from the row data
    precip_dict = dict(precipitation)
  
    
    print(f"Results for Precipitation - {precip_dict}")

    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all of the stations in the database"""

    # Design a query to calculate the total number of stations in the dataset
    results = session.query(station.id).count()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return data for the most active station (USC00519281)"""
    # Design a query to return data for most active station
    station_results = session.query(measurement.tobs).filter(measurement.station=='USC00519281')\
    .filter(measurement.date>='2016-08-23').all()

    session.close()

    tob_obs = []
    for date, tobs in station_results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tob_obs.append(tobs_dict)

    return jsonify(tob_obs)



@app.route("/api/v1.0/<start>")
def start():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the min, max, and average temps calculated from the given start date to the end of the dataset"""
    
    all_dates = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).all()

    session.close()

    all_temps = []
    for min_temp, avg_temp, max_temp in all_dates:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        all_temps.append(temps_dict)


    return jsonify(all_temps)


@app.route("/api/v1.0/<start>/<end>")
def start_end():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the min, max, and average temps calculated from the given start date to the given end date"""
    
    end_date = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    session.close()

    start_end_temps = []
    for min_temp, avg_temp, max_temp in end_date:
        se_temps_dict = {}
        se_temps_dict['Minimum Temperature'] = min_temp
        se_temps_dict['Average Temperature'] = avg_temp
        se_temps_dict['Maximum Temperature'] = max_temp
        start_end_temps.append(se_temps_dict)


    return jsonify(start_end_temps)



if __name__ == '__main__':
    app.run(debug=True)

