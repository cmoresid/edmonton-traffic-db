from model.site import Site
from model.traffic_event import TrafficEvent
from error.data_processor import NoDataTableFoundException
from xlrd import open_workbook
from datetime import datetime
from itertools import chain
import xlrd

class TrafficDataProcessor():
    DEFAULT_SITE_NUMBER_LOCATION = (2, 8)
    DEFAULT_ADT_LOCATION = (4, 8)
    DEFAULT_ADDRESS_LOCATION = (3, 8)
    SITE_TABLE_SEARCH_LOCATION = (1, 0)
    SITE_TABLE_SEARCH_LENGTH = 8
    
    TRAFFIC_DIRECTION_ROW_OFFSET = 2
    DATE_ROW_OFFSET = 1
    DATE_COLUMN_OFFSET = 3
    TIME_ROW_OFFSET = 3
    DIRECTION_COLUMN_OFFSET = 2

    HOURS_IN_DAY = 24
    TRAFFIC_SHEET_INDEX = 0
    DIRECTION_COLUMN_COUNT = 2
    
    def __init__(self):
        self._current_file_name = ''
    
    def process_data_files(self, file_names):
        if type(file_names) != list:
            raise TypeError("file_names must be a list of file names.")
        
        return chain.from_iterable(map(self._process_data_file, file_names))
    
    def _process_data_file(self, file_name):
        print 'Processing %s' % (file_name,)

        self._current_file_name = file_name        
        
        spreadsheet_file = open_workbook(file_name)
        spreadsheet = spreadsheet_file.sheet_by_index(self.TRAFFIC_SHEET_INDEX)

        site_data = self._get_site_data_table(spreadsheet)
        site = Site(site_id=site_data['site_number'], \
            location=site_data['location'], \
            address=site_data['address'], \
            adt=site_data['adt'])
         
        start_row, start_col = self._find_data_table_start(spreadsheet)
        ncols = self._find_data_table_width(spreadsheet, start_row)
    
        if start_row == None and start_col == None:
            raise NoDataTableFoundException('Unable to find a data table in ' + file_name)
    
        date_row = start_row + self.DATE_ROW_OFFSET
        start_time_row = start_row + self.TIME_ROW_OFFSET
        end_time_row = start_time_row + self.HOURS_IN_DAY
        directions = ( \
            spreadsheet.cell(start_row + self.TRAFFIC_DIRECTION_ROW_OFFSET, 1), \
            spreadsheet.cell(start_row + self.TRAFFIC_DIRECTION_ROW_OFFSET, 2) \
        )
    
        events = []
        for day_index in range(1, ncols, self.DATE_COLUMN_OFFSET):
            for hour_index in range(start_time_row, end_time_row):
                date_time_tuple = xlrd.xldate_as_tuple(spreadsheet.cell(date_row, day_index).value, spreadsheet_file.datemode)
                date_time_tuple = date_time_tuple[:3] + (hour_index - start_time_row, 0)            
                direction_counts = spreadsheet.row_slice(hour_index, day_index, day_index + self.DIRECTION_COLUMN_OFFSET) 
            
                for i in range(self.DIRECTION_COLUMN_COUNT):
                    event = TrafficEvent(site=site)        
                    event.event_date_time = datetime(*date_time_tuple)
                    event.direction = directions[i].value
                    event.count = direction_counts[i].value

                    events.append(event)        
    
        return events
        
    def _find_data_table_start(self, spreadsheet):
        nrows = spreadsheet.nrows
    
        for row_index in range(nrows):
            cell_value = spreadsheet.cell(row_index, 1).value
        
            if cell_value != '':
                return (row_index, 1)
            
        return (None, None)

    def _find_data_table_width(self, spreadsheet, data_table_row_start):
        ncols = spreadsheet.ncols

        for col_index in range(1, ncols):
            cell_value = spreadsheet.cell(data_table_row_start, col_index).value

            if cell_value.lower().find('avg') != -1:
                return col_index

        return None
        
    def _get_site_data_table(self, spreadsheet):
        site_num = spreadsheet.cell(*self.DEFAULT_SITE_NUMBER_LOCATION).value
        
        if type(site_num) == float:
            return { \
                'site_number': site_num, \
                'address': spreadsheet.cell(*self.DEFAULT_ADDRESS_LOCATION).value, \
                'adt': spreadsheet.cell(*self.DEFAULT_ADT_LOCATION).value, \
                'location': None
            }
        else:
            return self._search_for_site_data_table(spreadsheet)

    def _search_for_site_data_table(self, spreadsheet):
        start_row, start_col = self.SITE_TABLE_SEARCH_LOCATION
        
        for row_index in range(self.SITE_TABLE_SEARCH_LENGTH):
            for col_index in range(spreadsheet.ncols):
                cell_value = spreadsheet.cell(row_index, col_index).value
                
                if type(cell_value) == unicode and cell_value.upper() == 'SITE NUMBER':
                    column_offset = col_index + 2
                    
                    return { \
                        'site_number': spreadsheet.cell(row_index, column_offset).value, \
                        'address': spreadsheet.cell(row_index+1, column_offset).value.strip(), \
                        'adt': spreadsheet.cell(row_index+2, column_offset).value, \
                        'location': None
                    }
        
        raise NoDataTableFoundException('Unable to find site table for \'%s\'' % (self._current_file_name,))
        
