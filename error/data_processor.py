class NoDataTableFoundError(Exception):
	"""Raised when the spreadsheet processor (an instance of TrafficDataProcessor) 
	cannot find the core traffic volume data table.
	"""
    pass
