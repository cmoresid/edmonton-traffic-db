# edmonton-traffic-db
Tool for importing Edmonton traffic volume data into a relational database:
http://www.edmonton.ca/transportation/traffic_reports/traffic-volumes-turning-movements.aspx

####Prerequisites Setup
You will need to setup some sort of relational database with geospatial capabilities in order to save the results of the extraction process. My suggestion is to use [PostGIS](http://postgis.net/install) which is a geospatial extension to a Postgres database. For Mac OS X, you can use [Postgres.app](http://postgresapp.com/). It includes the PostGIS extensions and the Postgres database.

Once you have your database installed and setup, be sure to update the connection string in the ``config.py`` file. See [SQLAlchemy Connection String Format](http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html) for the connection string format.

We make use of several Python modules, all of which can be installed using ``pip install -U <module_name>``. Here are the required Python modules:  
* Crypto
* geoalchemy2
* sqlalchemy
* geojson
* google-api-python-client
* httplib2
* pyOpenSSL

####Prerequisites Setup for Automatic Spreadsheet Download from Google Drive  

#####Google Dev Account Setup
In order to utilize the automatic spreadsheet download functionality, you will first need to setup a Google Dev Account that has the Google Drive API enabled on it. This step is *NOT* essential. You can always manually download all the spreadsheets and have the tool process them afterwards.

1. You will first need to create a project. Follow this link [here](https://console.developers.google.com/flows/enableapi?apiid=drive) to create new project.
2. Under the APIs & auth section, select 'Credentials'.
3. Select 'Create new Client ID'
4. Now select 'Installed Application' and select 'Other'.

Note the client ID and client secret. We will be needing them later.

#####Google Drive Setup
You will also need add the shared folders containing the traffic event spreadsheets to your Google Drive account. Apparently if you don't add the shared folder to your own account, the shared files will not show up when querying the folder with the API. Go figure...

1. Open the [Traffic Volume Data](http://www.edmonton.ca/transportation/traffic_reports/traffic-volumes-turning-movements.aspx) link.
2. Select one of the shared folder links (i.e. [001-010](https://docs.google.com/open?id=0B35cJTkjHnLNNGMwNTE3YzItYjcyZi00NTI5LThmMWMtOTE2ZTJiMjRiNWU2&start=0&num=10), [011-020](https://docs.google.com/open?id=0B35cJTkjHnLNNDY4MmY2NGQtOTZkYS00MWNjLWFiNzItMDI3MDZlNjFhMGEx&start=0&num=10), etc.
3. Login to the same account that you used to setup your Google Developer credentials.
4. Click the 'Add to Drive' button in the top right hand corner.

Repeat this with all the folders.

###How to Download All Traffic Volume Spreadsheets
1. Complete the prerequisites for automatic download from Google Drive (see above instructions).
2. Configure you ``CLIENT_ID`` and ``CLIENT_SECRET`` environmental variables.  
  a. In a bash shell, type ``export CLIENT_ID=<your client ID>`` in a command prompt to configure your ``CLIENT_ID``.
  b. In a bash shell, type ``export CLIENT_SECRET=<your client secret>`` in a command prompt to configure your ``CLIENT_SECRET``.
3. In the same bash shell you used to configure your environmental variables, type ``python main.py --download-all --output-dir=<output directory>`` where ``<output directory>`` is the path to the folder where you want to download the files.

###How to Import Traffic Volume Spreadsheets From Directory
1. Download some or all of the Traffic Volume Spreadsheets either automatically or manually from the City of Edmonton's website and place them into a directory. (The 'data' folder for example that is located in the source.)
2. In a bash shell, type ``python main.py --import-file=data``.

###To-Do
1. Match site locations with co-ordinates.

