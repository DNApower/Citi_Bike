
# coding: utf-8

# In[1]:

get_ipython().magic('matplotlib inline')
import pandas as pd
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import seaborn as sns



a = ['04', '05', '06','07', '08', '09']

alldock = pd.DataFrame()
for num in a:
    df = pd.read_csv("dockdata/TheOpenBus/2016-{}/bikeshare_nyc_raw.csv".format(num), sep="\t", error_bad_lines=False).iloc[:, :13]
    dock = df.loc[df['in_service'] == 1]
    dock = dock.drop('in_service', 1)
    dock = dock.drop('status_key', 1)
    df0 = dock[dock.pm == 1]
    df1 = dock[dock.pm == 0]
    df10 = df1[df1.hour != 12]
    df11 = df1[df1.hour == 12]
    df11['hour'] = 0
    df00 = df0[df0.hour != 12]
    df00['hour'] = df00['hour'] + 12
    df01 = df0[df0.hour == 12]
    dock = df10.append([df11,df00,df01])
    dock = dock.drop('pm', 1)
    dock['time'] = "20" + dock['date'] + " " + dock['hour'].astype(str) + ":" + dock['minute'].astype(str)
    dock['time']=dock['time'].map(lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M'))
    dock = dock.sort_index()
    dock['bike occupation ratio'] = dock['avail_bikes'] / (dock['avail_bikes'] + dock['avail_docks'])
    alldock = alldock.append(dock, ignore_index=True)
    print('This is month {}, the data number of the month is {}, the total numbe is {}'.format(num, len(dock), len(alldock)))

alldock = alldock.sort_values(by=['dock_id', 'time'], ascending=[True, True])
alldock.to_csv('Results/Dock_data.csv', index= False, sep=',')

# Take the station information into a indivisual file
station_info = alldock[['dock_id', 'dock_name', '_lat', '_long']].drop_duplicates()
station_info = station_info.dropna(axis=0, how='any')
station_info = station_info.loc[station_info['_lat'] > 40]
station_info.loc[station_info['_long'] > 40, '_long']= -73.977885
# Set new column names
cols = ['station id','station name','station latitude','station longitude']
station_info.columns = cols
station_info.to_csv('Results/station_names.csv', index= False, sep=',')
# Later have visual inspection in excel

# bike occupation ratio
bike_occupation_ratio  = alldock.groupby(['dock_id', 'date'])['bike occupation ratio'].mean().reset_index()
bike_occupation_ratio.to_csv('Results/bike_occupation_ratio_each_day.csv', index= False, sep=',')  
bike_occupation_ratio_station = bike_occupation_ratio.groupby(['dock_id'])['bike occupation ratio'].mean().reset_index()
cols = ['station id','daily bike occupation ratio']
bike_occupation_ratio_station.columns = cols
bike_occupation_ratio_station.to_csv('Results/bike_occupation_ratio_station_perday_station.csv', index= False, sep=',')

# Calculate timespan that station have no bike
alldock['time2'] = alldock.time
alldock['timedelta'] = (alldock['time']-alldock['time2'].shift()).fillna(0)
alldock.loc[alldock['timedelta'] < pd.Timedelta(0), 'timedelta'] = 0
alldock['timedelta_seconds'] = alldock['timedelta'].apply(lambda row: row.total_seconds())
alldock['empty rate'] = np.nan
alldock['empty rate'] = alldock['timedelta_seconds'] / (24*60*60)
alldock.loc[alldock['avail_bikes'] > 0, 'empty rate'] = 0
alldock.to_csv('Results/dock_data_percent_empty.csv', index= False, sep=',')
Percent_empty = alldock.groupby(['dock_id', 'date'])['empty rate'].sum().reset_index()
Percent_empty.to_csv('Results/dock_data_percent_empty_each_day.csv', index= False, sep=',')
Percent_empty_station = Percent_empty.groupby(['dock_id'])['empty rate'].mean().reset_index()
Percent_empty_station.to_csv('Results/dock_data_percent_empty_perday_station.csv', index= False, sep=',')


# Trip Data
b = [ '201604', '201605', '201606','201607', '201608', '201609']
for num in b:
    df = pd.read_csv("tripdata/{}-citibike-tripdata.csv".format(num))
    # Remove unnecessary columns
    df.drop(['usertype', 'birth year', 'gender', 'start station name', 'start station latitude',
            'start station longitude', 'end station name', 'end station latitude', 'end station latitude'], 1)   
    df['starttime'] = pd.to_datetime(df.starttime)
    df['stoptime'] = pd.to_datetime(df.stoptime)
    df.to_csv('Results/trips_{}.csv'.format(num), index= False, sep=',')
    print('This is month {}, the data number of the month is {}'.format(num, len(df)))

alltrip= pd.DataFrame()
for num in b:
    df = pd.read_csv('Results/trips_{}.csv'.format(num), sep=',')
    alltrip = alltrip.append(df)
    print('This is month {}'.format(num))
alltrip.to_csv('Results/All_trips_2016_summer.csv', index= False, sep=',')

alltrip['starttime'] = pd.to_datetime(alltrip.starttime)
alltrip['stoptime'] = pd.to_datetime(alltrip.stoptime)


# ### Calculate the Parking time ( Median parking time for a bike in the station)
ended_station=alltrip[['end station id', 'bikeid', 'stoptime']]
cols1 = ['station id', 'bikeid', 'stoptime']
ended_station.columns = cols1
start_station =alltrip[['start station id', 'bikeid', 'starttime']]
cols2 = ['station id', 'bikeid', 'starttime']
start_station.columns = cols2
station_trip = pd.merge(ended_station, start_station, how='left', on = ['station id','bikeid'])
station_trip.head()
# Calculate the difference between stoptime and starttime
station_trip['TimeDiff'] = station_trip['starttime'] - station_trip['stoptime']
station_trip = station_trip[station_trip.TimeDiff.notnull()]
station_trip = station_trip.drop(station_trip[station_trip['TimeDiff'] < pd.Timedelta(0)].index)
station_trip = station_trip.groupby(['station id', 'bikeid', 'stoptime'])['TimeDiff'].min().reset_index()
station_trip['TimeDiff_convert'] = station_trip['TimeDiff'].apply(lambda row: row.total_seconds())
station_trip.to_csv('Results/station_bike_parking_time_each_bike.csv', index = False, sep = ',')
station_trip_median = station_trip.groupby(['station id'])['TimeDiff_convert'].median().reset_index()
cols3 = ['station id', 'parking time']
station_trip_median.columns = cols3
station_trip_median.to_csv('Results/station_bike_parking_time_median.csv', index = False, sep = ',')
station_trip_median.head()


# Calculate the Daily rides counts and hourly rides rate 

alltrip['date'] = alltrip.starttime.dt.date
station_usage = alltrip.groupby(['start station id', 'date'])['tripduration'].count().reset_index()
station_usage = station_usage.groupby(['start station id'])['tripduration'].mean().reset_index()
cols4 = ['station id', 'rides_counts_daily']
station_usage.columns = cols4
station_usage.to_csv('Results/station_daily_rides_counts.csv', index = False, sep = ',')

cols4 = ['station id', 'percent empty']
Percent_empty_station.columns = cols4
rides_rate = pd.merge(Percent_empty_station, station_usage, how='inner', on=['station id'])
rides_rate['hourly_rides_rate'] = rides_rate['rides_counts_daily']/(24*(1-rides_rate['percent empty']))
rides_rate.to_csv('Results/station_daily_rides_counts.csv', index = False, sep = ',')

# Calculate the Daily parking counts
station_parking = alltrip.groupby(['end station id', 'date'])['tripduration'].count().reset_index()
station_parking = station_parking.groupby(['end station id'])['tripduration'].mean().reset_index()
cols5 = ['station id', 'parking_counts_daily']
station_parking.columns = cols5
station_parking.to_csv('Results/station_daily_parking_counts.csv', index = False, sep = ',')

# use daily bike occupation ratio  and Parking time to find unbalanced stations
station_info = pd.read_csv('Results/station_names_clean.csv', sep = ',')
station_identif = pd.merge(bike_occupation_ratio_station, station_trip_median, how='inner', on=['station id'])
station_identif = pd.merge(station_info, station_identif, how='inner', on=['station id'])
# 'daily bike occupation ratio'
station_identif['DBOR_Norm'] = (station_identif['daily bike occupation ratio'] - station_identif['daily bike occupation ratio'].mean())/ (station_identif['daily bike occupation ratio'].std())
# normalize 'log(Parking Time)'
station_identif['PT_Norm'] = (np.log(station_identif['parking time']) - np.log(station_identif['parking time']).mean())/ (np.log(station_identif['parking time']).std())

# Classifying stations
station_identif['Station_type'] = 'Balanced'
station_identif.loc[(station_identif['DBOR_Norm'] > 1) & (station_identif['PT_Norm'] > 1), 'Station_type']= 'LowDemand&HighSupply'
station_identif.loc[(station_identif['DBOR_Norm'] < -1 ) & (station_identif['PT_Norm'] < -1), 'Station_type']= 'HighDemand&LowSupply'
station_identif.to_csv('Results/Idenfifying_stations.csv', index=False, sep=',')

# How to rebalance

HighDemand_LowSupply = station_identif.loc[station_identif['Station_type'] == 'HighDemand&LowSupply']
HighDemand_LowSupply = HighDemand_LowSupply.drop(['daily bike occupation ratio', 
                                               'parking time', 'DBOR_Norm', 'PT_Norm'], 1)

LowDemand_HighSupply = station_identif.loc[station_identif['Station_type'] == 'LowDemand&HighSupply']
LowDemand_HighSupply = LowDemand_HighSupply.drop(['daily bike occupation ratio', 
                                               'parking time', 'DBOR_Norm', 'PT_Norm'], 1)


HighDemand_LowSupply = pd.merge(HighDemand_LowSupply, Percent_empty_station, how='left', on = ['station id'])
HighDemand_LowSupply = pd.merge(HighDemand_LowSupply, rides_rate, how='left', on = ['station id'])
HighDemand_LowSupply = pd.merge(HighDemand_LowSupply, station_parking, how='left', on = ['station id'])


LowDemand_HighSupply = pd.merge(LowDemand_HighSupply, Percent_empty_station, how='left', on = ['station id'])
LowDemand_HighSupply = pd.merge(LowDemand_HighSupply, rides_rate, how='left', on = ['station id'])
LowDemand_HighSupply = pd.merge(LowDemand_HighSupply, station_parking, how='left', on = ['station id'])


print("Stations lack bikes has {}".format(len(HighDemand_LowSupply)))
print("Stations lack rides has {}".format(len(LowDemand_HighSupply)))                                       


HighDemand_hourly_rides_rate = HighDemand_LowSupply['hourly_rides_rate'].mean()
HighDemand_percent_empty = HighDemand_LowSupply['percent empty_x'].mean()
HighDemand_parking_rate = HighDemand_LowSupply['parking_counts_daily'].mean()


LowDemand_hourly_rides_rate = LowDemand_HighSupply['hourly_rides_rate'].mean()
LowDemand_percent_empty = LowDemand_HighSupply['percent empty_x'].mean()
LowDemand_parking_rate = LowDemand_HighSupply['parking_counts_daily'].mean()
LowDemand_rides_counts_daily = LowDemand_HighSupply['rides_counts_daily'].mean()


b = [1, 10, 20, 30, 50, 60, 70, 80, 90, 100, 110, 120, 150]

y = []
emptytime = HighDemand_percent_empty
for x in b:
    emptytime = HighDemand_percent_empty
    t1 = ((1 - emptytime)*24/HighDemand_parking_rate)*x/50
    if t1 > emptytime:
        x = x - 1
        t1 = ((1 - emptytime)*24/HighDemand_parking_rate)*x/50
    else:
        y1 = HighDemand_hourly_rides_rate * ((1 - emptytime)*24/HighDemand_parking_rate)*x

    y.append(y1)


z = []
emptytime = LowDemand_percent_empty

for x in b:
    emptytime = LowDemand_percent_empty
    y1 = LowDemand_rides_counts_daily - LowDemand_hourly_rides_rate * ((1 - emptytime)*24/LowDemand_parking_rate)*(x/34)

    z.append(y1)    

demand_supply = pd.DataFrame(
    {'bike_number': b,
     'Increase Daily Rides': y,
     'Decreas Daily Rides': z
    })
demand_supply.to_csv('Results/demand_supply_analysis.csv', index = False, sep=',')


y2 = LowDemand_rides_counts_daily - LowDemand_hourly_rides_rate * ((1 - emptytime)*24/LowDemand_parking_rate)*(70/34)

y1 = HighDemand_hourly_rides_rate * ((1 - emptytime)*24/HighDemand_parking_rate)*70
print('By taking 70 bikes from 34 "low demand and high supply" stations to 50 "high demand and low supply" stations')
print('increase rides daily per station in 50 "high demand and low supply" stations is {}'.format(y1))
print('Only decrease rides daily per station in 34 "low demand and high supply" stations to {}'.format(y2))



