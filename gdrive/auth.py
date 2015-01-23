from os import environ
from httplib2 import Http
from error.gdrive import MissingGDriveCredentialsException
from oauth2client.client import OAuth2WebServerFlow

class GDriveAuth():
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive.readonly'
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    
    def __init__(self, client_id=None, client_secret=None):
        self._client_id = client_id \
            if client_id != None else environ.get('CLIENT_ID')
        self._client_secret = client_secret \
            if client_secret != None else environ.get('CLIENT_SECRET')
        
        if self._client_id == None:
            raise MissingGDriveCredentialsException(
                "Missing Client ID. Have you set the CLIENT_ID environmental variable?")
        if self._client_secret == None:
            raise MissingGDriveCredentialsException( \
                "Missing Client Secret. Have you set the CLIENT_SECRET environmental variable?") 

    def get_authenticated_http_client(self):
        flow = OAuth2WebServerFlow(self._client_id, self._client_secret, self.OAUTH_SCOPE,
                           redirect_uri=self.REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        
        print 'Go to the following link in your browser: ' + authorize_url
        code = raw_input('Enter verification code: ').strip()
        
        credentials = flow.step2_exchange(code)
        
        return credentials.authorize(Http())
        
        