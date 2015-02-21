# Hosted Edmonton Traffic DB
Currently, the data can be accessed from an Amazon EC2 instance. Here is the connection information:

**Host** - ec2-52-0-53-5.compute-1.amazonaws.com  
**Port** - 5432   
**User Name** - gisdb_user   
**Password** - XAAz64TtYc 

You can also explore the data via phpPgAdmin:  
http://ec2-52-0-53-5.compute-1.amazonaws.com/phpPgAdmin/

##Main Table Structure  
**Site Table**  
* site_id : A unique identifier to identify the site monitoring location.  
* address : The address of the site monitoring location.  
* adt : The average daily traffic that a site encounters. 
* street_type : The type of street.  
* category : Describes the mechanism used by / purpose of the site.  
* in_service : Describes when the site monitor was established.  
* county : The county where the site monitor is located.  
* jursidiction : Similar to county.  
* primary_purpose : Describes the purpose of the site monitoring location.  

**Traffic Event Table**
* site_id : The foreign key that reference which site the event took place.  
* event_date_time : Describes the date and time the event took place. Each event entry represents an hour of time.
* direction : The direction of traffic that was being monitored.  
    * EBD - East Bound  
    * WBD - West Bound  
    * NBD - North Bound 
    * SBD - South Bound  
* count : The number of vechicles that were recorded during the 1 hour period.

## Useful Views
The following views may be helpful:

**all_sites** - Returns all the site locations with the co-ordinates formatted in a 'latitude,longitude' format. Useful if you want to plug the co-ordinates into Google Maps.  
**all_sites_coords** - Returns all the site locations with separate columns for latitude and longitude along with some other metadata describing the site monitoring locations.  

### Disclaimer
The data has been gathered from a variety sources. The some of the sources used to create this database are known  
to have data integrity problems. Some of the co-ordinates for the site monitoring locations have been matched from an
offical source, while other site monitoring location co-ordinates have been retrieved using ArcGIS. The site location  
co-ordinates will therefore be approximate.
