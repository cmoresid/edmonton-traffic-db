from processor.traffic_data_import import TrafficDataDBImport

if __name__ == "__main__":
    importer = TrafficDataDBImport()
    
    importer.traffic_data_import(['data/ABRoad.xls'])
    