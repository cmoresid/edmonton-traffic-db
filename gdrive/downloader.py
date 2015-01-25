from gdrive.auth import GDriveAuth 
from apiclient.discovery import build
import tempfile, os, config

class GDriveDownloadResult():
    """Contains the results of a spreadsheet download from
    Google Drive.
    """
    def __init__(self, file_id, success, message):
        """Initializes a GDriveDownloadResult object with the
        file ID, the success of the download, and a message.

        Keyword arguments:
        file_id -- The Google Drive file ID.
        success -- Whether or not the download was succesful.
        message -- A string message regarding the download result.
        """
        self.file_id = file_id
        self.success = success
        self.message = message

class GDriveDownloader():
    """An ochestration class which interacts with the Google
    Drive API to handle the downloading of files.
    """  
    def __init__(self, http_client=None, output_dir=tempfile.mkdtemp()):
        """Initializes a GDriveDownloader object with an authenticated
        http client and an output directory to save the downloaded files.

        Keyword arguments:
        http_client -- An HTTP client that has been authenticated with
                       Google Drive API. One can be obtained from
                       GDriveAuth#get_authenticated_http_client.
        output_dir -- The directory to save the downloaded files. Can be
                      an absolute path or a relative path.
        """
        # If http_client is not specified, automatically create one
        # using the credentials stored in the CLIENT_ID and CLIENT_SECRET
        # environmental variables.
        http = http_client if http_client != None \
            else GDriveAuth().get_authenticated_http_client()
        
        self.output_dir = output_dir

        # Create the service to interact with the Google Drive
        # API.
        self._service = build('drive', config.settings['gdrive_api_version'], http=http)
    
    def download_file(self, drive_file):
        """Downloads the actual file represented by the drive_file parameter.

        Borrowed from: https://developers.google.com/drive/v2/reference/files/get

        Keyword arguments:
        drive_file --   
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
        """
        """
        drive_file = self._service.files().get(fileId=file_id).execute()
        
        return self.download_file(drive_file)
            
    def download_files_in_folder(self, folder_id):
        """
        """
        drive_folder = self._service.files().list(q="'%s' in parents" % (folder_id,), 
                                                fields='items(id,downloadUrl,originalFilename),nextPageToken').execute()
        files = drive_folder.get('items', [])
        
        return map(self.download_file, files)
        
    def display_results(self, download_results):
        """
        """

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
