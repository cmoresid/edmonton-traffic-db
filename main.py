from processor.traffic_data_import import TrafficDataDBImport
import os

if __name__ == "__main__":
    importer = TrafficDataDBImport()
    
    spreadsheets = [os.path.join('data', f) for f in os.listdir('data') if os.path.join('data',f).endswith('.xls') ]
    importer.traffic_data_import(spreadsheets)
    