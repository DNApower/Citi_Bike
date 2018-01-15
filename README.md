# Citi_Bike
Citi Bike is a very convenient way to commute in the New York City. However, the system itself suffers imbalance of bikes due to the popularity of different stations.  Thus rebalancing the system is necessary. This project used **the daily bike occupation ratio** and **parking time** as the key metrics to identify imbalanced stations (high bike occupation and long parking time stations vs. low bike occupation and short parking time stations) among the 511 stations from April to September at 2016.   A rebalancing strategy by removing bikes from high bike occupation and long parking time stations to low bike occupation and short parking time stations was then proposed. 

## Data Source
1. The bike trip data from [Citi bike system data](https://www.citibikenyc.com/system-data) is used to calculate the parking time of a bike at each station.
2. The docker data collteced by [TheOpenBuss](https://www.theopenbus.com/) is used to calculate the daily bike occupation ratio.

## Result
![Daily bike occupation ratio and parking time at each station](/images/stations.png)
