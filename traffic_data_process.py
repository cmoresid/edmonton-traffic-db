from ORM import Site, TrafficEvent
from xlrd import open_workbook
from datetime import datetime
import xlrd

site_number_cell = (2, 8)
adt_location_cell = (4, 8)

def process_data_files(file_names):
    for file_name in file_names:
        return process_data_file(file_name)
        
def process_data_file(file_name):
    spreadsheet_file = open_workbook(file_name)
    spreadsheet = spreadsheet_file.sheet_by_index(0)

    site_num = spreadsheet.cell(*site_number_cell).value
    location = 'POINT(4 1)' # Come back to later
    adt = spreadsheet.cell(*adt_location_cell).value
    site = Site(site_id=site_num, location=location, adt=adt)
    ncols = spreadsheet.ncols - 1 - 3
    
    events = []
    for day_index in range(1, ncols, 3):
        for hour_index in range(15, 39):
            date_time_tuple = xlrd.xldate_as_tuple(spreadsheet.cell(13, day_index).value, spreadsheet_file.datemode)
            date_time_tuple = date_time_tuple[:3] + (hour_index - 15, 0)            
            direction_counts = spreadsheet.row_slice(hour_index, day_index, day_index + 2) 
            
            for i in range(2):
                event = TrafficEvent(site=site)        
                event.event_date_time = datetime(*date_time_tuple)
                event.direction = i
                event.count = direction_counts[i].value

                events.append(event)        
    
    return events
        
