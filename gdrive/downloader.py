from gdrive.auth import GDriveAuth 
from apiclient.discovery import build
import tempfile
import os

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
        file_destination = os.path.join(self.output_dir, drive_file.get('title'))
        file_id = drive_file.get('id')
        
        if os.path.exists(file_destination):
            return GDriveDownloadResult(file_id, False, "%s exist; do not download." % (file_destination,))
        
        download_url = drive_file.get('downloadUrl')
        if download_url:
            resp, content = self._service._http.request(download_url)
            
            if resp.status == 200:
                file_destination = os.path.join(self.output_dir, drive_file.get('title'))
                
                with open(file_destination, 'w+') as output_file:
                    output_file.write(content)
                    
                return GDriveDownloadResult(file_id, True, file_destination)
            else:
                return GDriveDownloadResult(file_id, False, 'No download url.')
        else:
            # The file doesn't have any content stored on Drive.
            return GDriveDownloadResult(file_id, False, 'No content stored on Drive.')
            
    def download_files_in_folder(self, folder_id):
        drive_folder = self._service.files.list(q="'%s' in parents" % (folder_id,), 
                                                fields='items(id,downloadUrl,originalFilename),nextPageToken')
        files = drive_folder.get('items', [])
        
        return map(self.download_file, files)
        
    
            
            
    

            
    
        
    
    
            