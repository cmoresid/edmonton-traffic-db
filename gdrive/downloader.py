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
        drive_file --  A DTO object created by the Google Drive API that represents
                       a file on Google Drive to be downloaded.
        """       
        file_destination = os.path.join(self.output_dir, drive_file.get('originalFilename'))
        file_id = drive_file.get('id')
        
        # Don't download a file that already exists on the file system.
        if os.path.exists(file_destination):
            return GDriveDownloadResult(file_id, False, "%s already exists." % (file_destination,))
        
        download_url = drive_file.get('downloadUrl')
        if download_url:
            resp, content = self._service._http.request(download_url)

            if resp.status == 200:
                # Successfully retrieved file from Google Drive, now save it
                # to file system and return results.
                with open(file_destination, 'w+') as output_file:
                    output_file.write(content)
                    
                return GDriveDownloadResult(file_id, True, file_destination)
            else:
                # Unable to download file, return the status code of the request.
                return GDriveDownloadResult(file_id, False, 'Unable to download file: %d', resp.status)
        else:
            # The file doesn't have any content stored on Drive.
            return GDriveDownloadResult(file_id, False, 'No content stored on Drive.')
            
    def download_file_by_id(self, file_id):
        """Downloads the file associated with the file ID argument."""
        # Retrieve the file meta data from Google Drive.
        drive_file = self._service.files().get(fileId=file_id).execute()
        
        # Now actually download the file from Google Drive.
        return self.download_file(drive_file)
            
    def download_files_in_folder(self, folder_id):
        """Downloads all the files inside the folder associated with the folder ID."""
        # Get a list of all the files' metadata stored in the specified
        # Google Drive folder ID.
        drive_folder = self._service.files().list(q="'%s' in parents" % (folder_id,), 
                                                fields='items(id,downloadUrl,originalFilename),nextPageToken').execute()
        # Only field we care about is the items field.
        files = drive_folder.get('items', [])
        
        # Download each file located inside the folder. 
        return map(self.download_file, files)
