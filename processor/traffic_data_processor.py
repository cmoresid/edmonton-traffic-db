from model.site import Site
from model.traffic_event import TrafficEvent
from error.data_processor import NoDataTableFoundError
from xlrd import open_workbook
from datetime import datetime
from itertools import chain
import xlrd

class TrafficDataProcessor():
    """Orchestration class that will read in the spreadsheets
    containing the traffic volume data and parse the data and
    then transform it into in-memory representations that can
    be stored in a database.
    """
    # The most common cell location for site number.
    DEFAULT_SITE_NUMBER_LOCATION = (2, 8)
    # The most common cell location for average daily volume.
    DEFAULT_ADT_LOCATION = (4, 8)
    # The most common cell location for site address.
    DEFAULT_ADDRESS_LOCATION = (3, 8)
    # Default location to start search for the group of cells
    # that contain the site information.
    SITE_TABLE_SEARCH_LOCATION = (1, 0)
    # The maximum number of columns to search by
    SITE_TABLE_SEARCH_LENGTH = 8
    # Number of rows to add to the start row of the 
    # traffic event data table to find the Date information.
    DATE_ROW_OFFSET = 1
    # Number of columns to add to the start column of the 
    # traffic event data table to find the next group of
    # events
    DATE_COLUMN_OFFSET = 3
    # Number of rows to add to the start row of the traffic
    # event data table to find the start of the time information.
    TIME_ROW_OFFSET = 3
    # The number of time events in the traffic event data.
    HOURS_IN_DAY = 24
    # The sheet number that usually contains the traffic volume
    # data. Sometimes it will be the second sheet though.
    DEFAULT_TRAFFIC_SHEET_INDEX = 0
    
    def __init__(self):
        """Initializes a new instance of a TrafficDataProcessor."""
        self._current_file_name = ''
    
    def process_data_files(self, file_names):
        """Extracts traffic event information from all the spreadsheets
        specified in the file_names parameter and creates an in-memory
        representation of the traffic events and sites.

        Keyword arguments:
        file_names -- A list of file paths for spreadsheets to process.
        """
        # Verify that argument is actually a list.
        if type(file_names) != list:
            raise TypeError("file_names must be a list of file names.")
        
        # Return a flattened list of all the traffic events processed in all
        # the spreadsheets specified by the file_names parameter.
        return chain.from_iterable(map(self._process_data_file, file_names))
    
    def _process_data_file(self, file_name):
        """Extracts traffic event information from the specified spreadsheet
        and creates an in-memory representation of the traffic events and
        sites.

        Keyword arguments:
        file_name -- The file path for the spreadsheet to process.
        """
        print 'Processing %s' % (file_name,)

        self._current_file_name = file_name        
        
        spreadsheet_file = open_workbook(file_name)
        # Find the sheet that contains the traffic data information.
        spreadsheet = self._get_site_data_sheet(spreadsheet_file)

        # Extract the site information for the group traffic events and
        # store in Site object.
        site_data = self._get_site_data_table(spreadsheet)
        site = Site(site_id=site_data['site_number'], \
            location=site_data['location'], \
            address=site_data['address'], \
            adt=site_data['adt'])
         
        # Determine where traffic event data table starts within the
        # spreadsheet. It's not always in the same spot.
        start_row, start_col = self._find_data_table_start(spreadsheet)
        # Find out the width of the traffic event data table.
        ncols = self._find_data_table_width(spreadsheet, start_row)
    
        # Return an error if the traffic event data table cannot be found.
        if start_row == None and start_col == None:
            raise NoDataTableFoundException('Unable to find a data table in ' + file_name)
    
        # Calculate where the date information is contained.
        date_row = start_row + self.DATE_ROW_OFFSET
        # Calculate where the time information is contained.
        start_time_row = start_row + self.TIME_ROW_OFFSET
        # Calculate the end of where the time information is contained.
        end_time_row = start_time_row + self.HOURS_IN_DAY
        # Determine the offset for the different days in the table.
        date_column_offset = self._get_date_column_offset(spreadsheet, start_row)
        # Calculate how many directions (i.e. SB, NB, EB, WB) are being
        # tracked.
        direction_factor_count = date_column_offset-1

        events = []
        # First, iterate from left-to-right, grouping by the day
        # of the week.
        for day_index in range(1, ncols, date_column_offset):
            # Now iterate from top-to-bottom which represents the time
            # of each respective day.
            for hour_index in range(start_time_row, end_time_row):
                # Extract the raw date/time from the header, ignoring the incorrect
                # time component.
                date_time_tuple = xlrd.xldate_as_tuple(spreadsheet.cell(date_row, day_index).value, spreadsheet_file.datemode)
                # Transform the raw date/time to represent the correct time and date.
                date_time_tuple = date_time_tuple[:3] + (hour_index - start_time_row, 0)
                # Create a slice containing the directional traffic counts for the particular time of day.        
                direction_counts = spreadsheet.row_slice(hour_index, day_index, day_index + direction_factor_count) 

                # Iterate through the directional traffic counts and create
                # a traffic event object for each directional count.
                for i in range(1, direction_factor_count+1):
                    event = TrafficEvent(site=site)        
                    event.event_date_time = datetime(*date_time_tuple)
                    event.direction = spreadsheet.cell(start_row + 2, i).value
                    # Some spreadsheets contain a '-' to indicate 0. Replace the '-'
                    # with a 0.
                    event.count = self._sanitize_count_value(direction_counts[i-1].value)

                    events.append(event)        
    
        return events
        
    def _find_data_table_start(self, spreadsheet):
        """Returns a tuple containing the indices of where the traffic 
        event data table starts within the sheet.

        Keyword arguments:
        spreadsheet -- The spreadsheet to search through.
        """
        nrows = spreadsheet.nrows
    
        for row_index in range(nrows):
            cell_value = spreadsheet.cell(row_index, 1).value
        
            if cell_value != '':
                return (row_index, 1)
            
        return (None, None)

    def _find_data_table_width(self, spreadsheet, data_table_row_start):
        """Returns an integer describing how many columns are within the
        traffic event data table.
        """
        ncols = spreadsheet.ncols

        for col_index in range(1, ncols):
            cell_value = spreadsheet.cell(data_table_row_start, col_index).value

            # Ignore the Avg. column found within the spreadsheets. We can
            # calculate that ourselves once the data is in the data base.
            if cell_value.lower().find('avg') != -1:
                return col_index

        return None
    
    def _get_site_data_sheet(self, workbook):
        """Returns the sheet that contains the traffic event data."""
        try:
            # On some spreadsheets, the first sheet contains a bunch of
            # line graphs. We want to ignore those and extract the raw
            # data.
            sheet = workbook.sheet_by_name('TCM.Export')
            sheet = workbook.sheet_by_index(1)
        except:
            sheet = workbook.sheet_by_index(self.DEFAULT_TRAFFIC_SHEET_INDEX)

        return sheet

    def _get_date_column_offset(self, spreadsheet, data_table_row_start):
        """Return an integer describing the width of each group of events
        by time and direction.
        """
        direction_row_start = data_table_row_start + 2
        date_column_offset = 1
        done_counting = False

        while not(done_counting):
            if spreadsheet.cell(direction_row_start, date_column_offset).value != 'Total':
                date_column_offset = date_column_offset + 1
            else:
                done_counting = True

        return date_column_offset

    def _get_site_data_table(self, spreadsheet):
        """Returns a dictionary containing the site information.

        Keyword arguments:
        spreadsheet -- The spreadsheet to search through.
        """
        site_num = spreadsheet.cell(*self.DEFAULT_SITE_NUMBER_LOCATION).value

        # Some site numbers contain a letter at the end of them, so we must
        # cast all of the site numbers to be strings.
        if type(site_num) == float:
            site_num = str(int(site_num))
        
        # The site number will only be 7 characters long
        # if there is an additional letter at the end of it.
        if len(site_num) == 6 or len(site_num) == 7:
            return { \
                'site_number': site_num, \
                'address': spreadsheet.cell(*self.DEFAULT_ADDRESS_LOCATION).value, \
                'adt': spreadsheet.cell(*self.DEFAULT_ADT_LOCATION).value, \
                'location': None
            }
        else:
            # Site information is not in the conventional place, search
            # for it manually.
            return self._search_for_site_data_table(spreadsheet)

    def _sanitize_count_value(self, count_value):
        """Ignore any non-numeric values and return a 0 instead.

        Keyword arguments:
        count_value -- The value to sanatize.
        """
        return count_value if type(count_value) == float else 0

    def _search_for_site_data_table(self, spreadsheet):
        """Returns a dictionary containing the site information
        contained within the spreadsheet.

        Keyword arguments:
        spreadsheet -- The spreadsheet to search through.
        """
        # Define the location to start searching from.
        start_row, start_col = self.SITE_TABLE_SEARCH_LOCATION
        
        for row_index in range(self.SITE_TABLE_SEARCH_LENGTH):
            for col_index in range(spreadsheet.ncols):
                cell_value = spreadsheet.cell(row_index, col_index).value
                
                if type(cell_value) == unicode and cell_value.upper() == 'SITE NUMBER':
                    column_offset = col_index + 2
                    site_num = spreadsheet.cell(row_index, column_offset).value

                    if type(site_num) == float:
                        site_num = str(int(site_num))

                    return { \
                        'site_number': site_num, \
                        'address': spreadsheet.cell(row_index+1, column_offset).value.strip(), \
                        'adt': spreadsheet.cell(row_index+2, column_offset).value, \
                        'location': None
                    }
        
        raise NoDataTableFoundError('Unable to find site table for \'%s\'' % (self._current_file_name,))
        
