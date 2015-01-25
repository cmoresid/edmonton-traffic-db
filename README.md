# edmonton-traffic-db
Tool for importing Edmonton traffic volume data into a relational database:
http://www.edmonton.ca/transportation/traffic_reports/traffic-volumes-turning-movements.aspx

####Prerequisites Setup
You will need to setup some sort of relational database with geospatial capabilities in order to save the results of the extraction process. My suggestion is to use [PostGIS](http://postgis.net/install) which is a geospatial extension to a Postgres database. For Mac OS X, you can use [Postgres.app](http://postgresapp.com/). It includes the PostGIS extensions and the Postgres database.

We make use of several Python modules, all of which can be installed using ``pip install -U <module_name>``. Here are the required Python modules:  
* Crypto
* geoalchemy2
* sqlalchemy
* geojson
* google-api-python-client
* httplib2
* pyOpenSSL

###How to Use  
1. Specify the connection string to your database in the ``config.py`` file. [SQLAlchemy Format](http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html)
2. Download a spreadsheet from the website on to your local computer.
3. In the ``main.py`` file, specify the path for the spreadsheet you downloaded in the following line: ``importer.traffic_data_import(['path/to/spreadsheet.xls'])``.
4. Run from the commandline ``python main.py``


###To-Do
1. Document code.
2. Create table to track imported data.
