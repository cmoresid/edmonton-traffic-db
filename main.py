#!/usr/bin/env python

from processor.traffic_data_import import TrafficDataDBImport
import sys
import getopt

class CommandLineMain():
	def main(self, argv):
		try:
			opts, args = getopt.getopt(argv, '', ['download-all', \
				'download-folder=', 'download-file', 'import-file', 'import-folder'])
		except getopt.GetoptError:
			self.print_usage()
			sys.exit(2)

		is_valid, message = self.validate_args(opts)

		if not(is_valid):
			print message
			sys.exit(2)

		for opt, arg in opts:
			pass

		#importer = TrafficDataDBImport()

    	#spreadsheets = [os.path.join('data', f) for f in os.listdir('data') if os.path.join('data',f).endswith('.xls')]
    	#importer.traffic_data_import(spreadsheets)

	def print_usage(self):
		print 'usage: python main.py [--download-all] [--download-folder=folderId] [--download-file=fileId]'
		print '                      [--output-dir=folderPath]'
		print '                      [--import-folder=folderPath] [--import-file=filePath]'
		print ''
		print 'options:'
		print ''
		print '--download-all'
		print '\tDownloads all the spreadsheets from all the folders specified in the'
		print '\t\'edmonton-data-folder-ids\' dictionary defined in config.py. This is the'
		print '\tdefault action if no parameters are specified.'
		print ''
		print '--download-folder=folderId'
		print '\tDownload all the spreadsheets located in the Google Drive folder. The'
		print '\tfolder ID will be an alpha-numeric string of 61 characters.'
		print ''
		print '--download-file=fileId'
		print '\tDownload the spreadsheet file corresponding to the given fildId. The'
		print '\tfile ID will be an alpha-numeric string of 61 characters.'
		print ''
		print '--output-dir=folderPath'
		print '\tUsed in conjunction with the --download-all, --download-folder, or'
		print '\t--download-file options to specify where the spreadsheets will be'
		print '\tdownloaded to.'
		print ''
		print '--import-folder=folderPath'
		print '\tImports all the spreadsheets in specified folder into the database.'
		print ''
		print '--import-file=filePath'
		print '\tImports the spreadsheet specified by the filePath parameter into the'
		print '\tdatabase.'
		print ''

if __name__ == "__main__":
	driver = CommandLineMain()
	driver.main(sys.argv[1:])

