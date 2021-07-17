import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.schema import MetaData 
import datetime as dt
from flask import Flask, jsonify

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
#creating a session link from Python
session = Session(engine)
#setting up Flask
recent_date = session.query(Measurement.date).order_by(Measurement.date).first().date
twelve_months_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
session.close()


@app.route("/")
def welcome():
    """Listing all available api routes"""
    return(
        f"Availabile Routes: <br>"
        f"/api/v1.0/precipitation <br>"
        f"/api/v1.0/stations <br>"
        f"/api/v1.0/tobs <br>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Perform a query to retrieve the data and precipitation scores
    precepitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > twelve_months_ago).\
        order_by(Measurement.date).all()

    session.close()
    prcp_results= dict(precepitation_data)
    return jsonify(prcp_results)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    results = session.query(Station.station).all()
    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobos():
    # Query the dates and temperature observations of the most active station for the last year of data
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    session.close()
    stations_stats = active_stations[0][0]
    t_results = session.query(Measurement.station, Measurement.tobs).\
                filter(Measurement.station == stations_stats).\
                filter(Measurement.date >= twelve_months_ago).all()
    session.close()

    temps = list(np.ravel(t_results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    session.close()

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        session.close()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

            
if __name__ == '__main__':
    app.run()