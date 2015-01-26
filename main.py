#!/usr/bin/env python

from processor.traffic_data_import import TrafficDataDBImport
from gdrive.downloader import GDriveDownloader
import sys, getopt, config, os

class CommandLineMain():
	def main(self, argv):
		try:
			opts, args = getopt.getopt(argv, '', ['download-all', \
				'download-folder=', 'download-file=', 'import-file=', 'import-folder=', \
				'output-folder='])
			self.validate_args(opts)
		except getopt.GetoptError:
			self.print_usage()
			sys.exit(2)

		if len(filter(lambda x: x[0].startswith('--download'), opts)) > 1:
			output_dir = self.get_output_folder(opts)
		
		# Sort arguments by order of dependence, which
		# just happens to be alphabetical.
		opts = sorted(opts, key=lambda k: k[0])

		for opt, arg in opts:
			if opt == '--download-all':
				self.download_all(output_dir)
			elif opt == '--download-folder':
				self.download_folder(arg, output_dir)
			elif opt == '--download-file':
				self.download_file(arg, output_dir)
			elif opt == '--import-folder':
				self.import_folder(arg)
			elif opt == '--import-file':
				self.import_file(arg)

	def validate_args(self, opts):
		options = map(lambda item: item[0], opts)

		if len(filter(lambda x: x.startswith('--download'), options)) > 1:
			raise RuntimeError('You can only specify one download-type argument.')
		elif len(filter(lambda x: x.startswith('--import'), options)) > 1:
			raise RuntimeError('You can only specify one import-type argument.')
		elif '--download-all' in options and not('--output-folder' in options):
			raise RuntimeError('You must specify an output folder.')
		elif '--download-folder' in options and not('--output-folder' in options):
			raise RuntimeError('You must specify an output folder.')
		elif '--download-file' in options and not('--output-folder' in options):
			raise RuntimeError ('You must specify an output folder.')
		elif '--import-file' in options or '--import-folder' in options:
			self.validate_path(filter(lambda x: x[0].startswith('--import'), opts)[0][1], \
				"The import path does not exist.")

	def download_all(self, output_folder):
		downloader = GDriveDownloader(output_dir=output_folder)

		results = map(downloader.download_files_in_folder, \
			config.settings['edmonton-data-folder-ids'].values())


	def download_folder(self, folder_id, output_folder):
		downloader = GDriveDownloader(output_dir=output_folder)
		results = downloader.download_files_in_folder(folder_id)

	def download_file(self, file_id, output_folder):
		downloader = GDriveDownloader(output_dir=output_folder)
		results = downloader.download_file_by_id(file_id)

	def import_folder(self, folder_path):
		spreadsheets = [os.path.join('data', f) for f in os.listdir('data') \
			if os.path.join('data',f).endswith('.xls')]

		importer = TrafficDataDBImport()
		importer.traffic_data_import(spreadsheets)

	def import_file(self, file_path):
		importer = TrafficDataDBImport()
		importer.traffic_data_import([file_path])

	def get_output_folder(self, opts):
		output_folder = filter(lambda opt: opt[0] == '--output-folder', opts)[0][1]

		if not(os.path.exists(output_folder)):
			raise RuntimeError('The specified output folder does not exist.')

		return output_folder

	def validate_path(self, path, message):
		if not(os.path.exists(path)):
			raise RuntimeError(message)

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
		print '--output-folder=folderPath'
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
