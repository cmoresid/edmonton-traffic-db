# edmonton-traffic-db
Tool for importing Edmonton traffic volume data into a relational database:
http://www.edmonton.ca/transportation/traffic_reports/traffic-volumes-turning-movements.aspx

###How to Use  

1. Specify the connection string to your database in the ``config.py`` file. (sqlalchemy format)
2. Download a spreadsheet from the website on to your local computer.
3. In the ``main.py`` file, specify the path for the spreadsheet you downloaded in the following line: ``importer.traffic_data_import(['path/to/spreadsheet.xls'])``.
4. Run from the commandline ``python main.py``

###To-Do
1. Document code.
2. Create table to track imported data.
3. Ability to download spreadsheets right from google drive.
