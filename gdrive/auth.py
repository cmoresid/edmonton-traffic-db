from os import environ
from httplib2 import Http
from error.gdrive import MissingGDriveCredentialsError
from oauth2client.client import OAuth2WebServerFlow

class GDriveAuth():
    """Handles creating an authenticated client to connect
    with the Google Drive API.
    """

    # Defines the OAuth scope for API access. See
    # https://developers.google.com/drive/web/scopes for
    # available options.
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive.readonly'
    # This is the URI that Google's OAuth2 server will redirect you
    # to. URI is specific for installed apps.
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    
    def __init__(self, client_id=None, client_secret=None):
        """Initializes an instance of GDriveAuth with your
        Google Drive API client ID and client secret.

        If you choose not to define your client ID and client secret
        as arguments to the constructor, the constructor will check to
        see if 

        Keyword arguments:
        client_id -- Your Google Drive API client ID.
        client_secret -- Your Google Drive API client secret.
        """
        # See if CLIENT_ID and CLIENT_SECRET are defined 
        # as parameters. If not try to get both as environmental
        # variables. 
        self._client_id = client_id \
            if client_id != None else environ.get('CLIENT_ID')
        self._client_secret = client_secret \
            if client_secret != None else environ.get('CLIENT_SECRET')
        
        # Cannot proceed if credentials are missing.
        if self._client_id == None:
            raise MissingGDriveCredentialsError(
                "Missing Client ID. Have you set the CLIENT_ID environmental variable?")
        if self._client_secret == None:
            raise MissingGDriveCredentialsError( \
                "Missing Client Secret. Have you set the CLIENT_SECRET environmental variable?") 

    def get_authenticated_http_client(self):
        """Creates and returns an OAuth2 authenticated HTTP client.

        First, a URL will be created in order to generate an OAuth2 token. Go
        to the URL in your web browser. Choose an account to authenticate as. This
        account should have access to all the Edmonton Traffic Report Google Drive 
        folders.

        Second, a verification code will be generated in the web browser. Enter this
        code back into the command prompt. An authenticated HTTP client will be returned
        if successfully authenticated.
        """
        flow = OAuth2WebServerFlow(self._client_id, self._client_secret, self.OAUTH_SCOPE,
                           redirect_uri=self.REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        
        print 'Go to the following link in your browser: ' + authorize_url
        code = raw_input('Enter verification code: ').strip()
        
        credentials = flow.step2_exchange(code)
        
        return credentials.authorize(Http())
        
        