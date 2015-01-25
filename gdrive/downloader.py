from gdrive.auth import GDriveAuth 
from apiclient.discovery import build
import tempfile, os

class GDriveDownloadResult():
    def __init__(self, file_id, success, result):
        self.file_id = file_id
        self.success = success
        self.result = result

class GDriveDownloader():    
    def __init__(self, http_client=None, output_dir=tempfile.mkdtemp()):
        http = http_client if http_client != None else GDriveAuth()
        
        self.output_dir = output_dir
        self._service = build('drive', 'v2', http=http)
    
    def download_file(self, drive_file):
        """
            Borrowed from: https://developers.google.com/drive/v2/reference/files/get
        """       
        file_destination = os.path.join(self.output_dir, drive_file.get('originalFilename'))
        file_id = drive_file.get('id')
        
        if os.path.exists(file_destination):
            return GDriveDownloadResult(file_id, False, "%s already exists." % (file_destination,))
        
        download_url = drive_file.get('downloadUrl')
        if download_url:
            resp, content = self._service._http.request(download_url)
            
            if resp.status == 200:                
                with open(file_destination, 'w+') as output_file:
                    output_file.write(content)
                    
                return GDriveDownloadResult(file_id, True, file_destination)
            else:
                return GDriveDownloadResult(file_id, False, 'No download url.')
        else:
            # The file doesn't have any content stored on Drive.
            return GDriveDownloadResult(file_id, False, 'No content stored on Drive.')
            
    def download_file_by_id(self, file_id):
        drive_file = self._service.files().get(fileId=file_id).execute()
        
        return self.download_file(drive_file)
            
    def download_files_in_folder(self, folder_id):
        drive_folder = self._service.files().list(q="'%s' in parents" % (folder_id,), 
                                                fields='items(id,downloadUrl,originalFilename),nextPageToken').execute()
        files = drive_folder.get('items', [])
        
        return map(self.download_file, files)
        
    def display_results(self, download_results):
        downloaded = filter(lambda result: result.success, download_results)
        not_downloaded = filter(lambda result: not(result.success), download_results)
        
        print '----------------------------------------------------'
        print 'Successfully Downloaded'
        print '----------------------------------------------------'
        
        for gresult in downloaded:
            print '%s - Downloaded to %s' % (gresult.file_id,gresult.result)
            
        print '----------------------------------------------------'
        print 'Not Downloaded'
        print '----------------------------------------------------'
        
        for gresult in not_downloaded:
            print '%s - Not downloaded because "%s"' % (gresult.file_id, gresult.result)
