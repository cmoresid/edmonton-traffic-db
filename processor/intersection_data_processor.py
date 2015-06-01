from model.site import Site
from model.intersection_event import IntersectionEvent
from error.data_processor import NoDataTableFoundError
from xlrd import open_workbook
import datetime
from itertools import chain
from util.ordered_set import OrderedSet
import xlrd
import os


class TrafficIntersectionProcessor:
    """Orchestration class that will read in the spreadsheets
    containing the traffic volume data and parse the data and
    then transform it into in-memory representations that can
    be stored in a database.
    """
    # The most common cell location for intersection address.
    DEFAULT_ADDRESS_LOCATION = (2, 2)
    # Default location to start search for the group of cells
    # that contain the site information.
    SITE_TABLE_SEARCH_LOCATION = (0, 83)
    # The maximum number of columns to search by
    SITE_TABLE_SEARCH_LENGTH = 13
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

    def __parse_date(self, date_value):
        if date_value == u'':
            return None

        date_components = [int(i) for i in date_value.split('/')]

        return datetime(date_components[2], date_components[0], date_components[1])

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
        spreadsheet = spreadsheet_file.sheet_by_name('TCM.Export')
        ncols = spreadsheet.ncols
        nrows = spreadsheet.nrows

        turn_direction_events = []

        intersection_event_type = ''

        direction_event_type = ''
        intersection_event_type_row = 82

        for row in range(82, nrows):
            first_cell = spreadsheet.cell(row, 0)

            if first_cell.value == u'':
                continue
            elif first_cell.ctype == xlrd.XL_CELL_TEXT:
                intersection_event_type = first_cell.value.split(' ')[0]
                intersection_event_type_row = row
                continue
            else:
                intersection_event_date = datetime.datetime(*xlrd.xldate_as_tuple(
                    first_cell.value, spreadsheet_file.datemode))

            if intersection_event_type != 'Pedestrians':
                for col in range(1, ncols - 1):
                    if spreadsheet.cell(intersection_event_type_row, col).value != u'':
                        direction_event_type = spreadsheet.cell(intersection_event_type_row - 1, col).value\
                            .replace('(', '').replace(')', '')

                    intersection_event = IntersectionEvent()

                    # intersection_event.site_id = 0
                    intersection_event.event_type = intersection_event_type
                    intersection_event.event_date_time = intersection_event_date
                    intersection_event.direction = direction_event_type
                    intersection_event.turn_direction = spreadsheet.cell(intersection_event_type_row, col).value
                    intersection_event.count = int(spreadsheet.cell(row, col).value)

                    turn_direction_events.append(intersection_event)
            else:
                for col in range(1, ncols - 1):
                    if spreadsheet.cell(intersection_event_type_row, col).value != u'':
                        direction_event_type = spreadsheet.cell(intersection_event_type_row, col).value\
                            .replace('(', '').replace(')', '')

                    if spreadsheet.cell(row, col).value == '':
                        continue

                    intersection_event = IntersectionEvent()
                    intersection_event.event_type = intersection_event_type
                    intersection_event.event_date_time = intersection_event_date
                    intersection_event.direction = direction_event_type
                    intersection_event.turn_direction = ''
                    intersection_event.count = int(spreadsheet.cell(row, col).value)

                    turn_direction_events.append(intersection_event)

        return turn_direction_events


if __name__ == "__main__":
    spreadsheets = [os.path.join('../data/intersection', f) for f in os.listdir('../data/intersection')
                    if os.path.join('../data/intersection', f).endswith('.xls')]

    processor = TrafficIntersectionProcessor()
    processor.process_data_files(spreadsheets)

