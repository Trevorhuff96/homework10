import numpy as np
import pandas as pd
import datetime as dt 


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#?check_same_thread=False
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#sqlite:///Resources/hawaii.sqlite

Base = automap_base()
Base.prepare(engine , reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """ All available api routes"""

    return(
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value.
    Return the JSON representation of your dictionary """
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    sel = [Measurement.prcp,Measurement.date]

    most_recent_entry= session.query(*sel).order_by( Measurement.id.desc()).first()
    past12_months= session.query(*sel).all()

    #take the date of the most recent entry
    # most_recent_date=most_recent_entry[2]
    most_recent_date=most_recent_entry[1]
    
    #parse out the year from the string and subtract 1
    last_year=int(most_recent_date[:4])-1
    
    #replace most current year with the last year 
    one_year_ago=str(last_year)+most_recent_date[4:]
    
    # Perform a query to retrieve the data and precipitation scores
    qry2 = session.query(*sel).filter(Measurement.date <= most_recent_date).filter(Measurement.date >= one_year_ago)
    
    prec_dict={}
    for date_key in qry2:
        #since there are multiple date keys, you must append the the values to their respective keys using an array
        if date_key[1] in prec_dict:
            # append the new number to the existing array at this slot
            prec_dict[date_key[1]].append(date_key[0])
        else:
            # create a new array in this slot
            prec_dict[date_key[1]] = [date_key[0]]

    return jsonify(prec_dict)

@app.route("/api/v1.0/stations")
def stations():
    """ Return a JSON list of stations from the dataset """
    station_names = session.query(Station.station).all()
    list_names=list(np.ravel(station_names))
    return jsonify(list_names)

@app.route("/api/v1.0/<start>")
def start_date(start):
    interval_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    result=[]
    for internal_results in interval_date:
        result.append(internal_results[0])
        result.append(internal_results[1])
        result.append(internal_results[2])
    
    return jsonify(result)

@app.route("/api/v1.0/tobs")
def tobs():
    """ query for the dates and temperature observations from a year from the last data point. Return a JSON list of Temperature Observations (tobs) for the previous year"""
    # Query the last 12 months of temperature observation data for  all stations

    #find the last date for this station
    last_date= session.query(Measurement.date).order_by (Measurement.id.desc()).first()
    twelve_months_ago=int(last_date[0][:4])-1
    past_year=str(twelve_months_ago)+last_date[0][4:]
    past_year
    #Now retreive the past 12 months of temp data
    temp_year_data= session.query(Measurement.tobs).filter  (Measurement.date<=last_date[0]).filter(Measurement.date >= past_year).all()

    #parse through the query results and append tobs to a list
    temp_list=[]
    for data in temp_year_data:
        temp_list.append(data)

    return jsonify(temp_list)

@app.route("/api/v1.0/<start1>/<end1>")
def start_end(start1, end1):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive """
    interval_date1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start1).filter(Measurement.date <= end1).all()

    results=[]
    for internal_results1 in interval_date1:
        results.append(internal_results1[0])
        results.append(internal_results1[1])
        results.append(internal_results1[2])
    
    return jsonify(results)
        
    

if __name__ == "__main__":
    app.run(debug=True, port=5000)