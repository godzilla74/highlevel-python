import requests

from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session
from typing import Optional, Union, Dict, Any

from highlevel.exceptions import UnauthorizedError, WrongFormatInputError


class Client(object):
    """Interface to interact with the HighLevel API."""

    URL: str = "https://api.highlevel.com/"
    AUTH_URL: str = "https://api.highlevel.com/oauth/authorize"
    TOKEN_URL: str = "https://api.highlevel.com/oauth/token"
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, redirect_uri: Optional[str] = None) -> None:
        """Initializes the Client class.

        Args:
            client_id (str, optional): Client ID. Defaults to None.
            client_secret (str, optional): Client secret key. Defaults to None.
            redirect_uri (str, optional): Redirect URI. Defaults to None.
        """
        self.CLIENT_ID: Optional[str] = client_id
        self.CLIENT_SECRET: Optional[str] = client_secret
        self.REDIRECT_URI: Optional[str] = redirect_uri
        self.TOKEN: Optional[Dict[str, Any]] = None

    def authorization_url(self, state: Optional[str] = None) -> str:
        """Generates the authorization URL for authentication.

        Args:
            state (str, optional): Optional state to maintain session integrity. Defaults to None.

        Returns:
            str: Authorization URL.
        """
        params: Dict[str, Optional[str]] = {
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
            "state": state,
        }
        return self.AUTH_URL + "?" + urlencode(params)

    def get_access_token(self, code: str) -> Dict[str, Any]:
        """Obtains the access token using the authorization code.

        Args:
            code (str): Authorization code.

        Returns:
            Dict[str, Any]: Access token.
        """
        highlevel = OAuth2Session(self.CLIENT_ID, redirect_uri=self.REDIRECT_URI)
        self.TOKEN = highlevel.fetch_token(self.TOKEN_URL, code=code, client_secret=self.CLIENT_SECRET)
        self.set_token(self.TOKEN)
        return self.TOKEN

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refreshes the access token using the refresh token.

        Args:
            refresh_token (str): Refresh token.

        Returns:
            Dict[str, Any]: Refreshed access token.
        """
        highlevel = OAuth2Session(self.CLIENT_ID, redirect_uri=self.REDIRECT_URI, token={'refresh_token': refresh_token})
        self.TOKEN = highlevel.refresh_token(self.TOKEN_URL, client_id=self.CLIENT_ID, client_secret=self.CLIENT_SECRET)
        self.set_token(self.TOKEN)
        return self.TOKEN

    def set_token(self, access_token: Dict[str, Any]) -> None:
        """Sets the authorization token in the headers.

        Args:
            access_token (Dict[str, Any]): Access token.
        """
        self.headers.update(Authorization=f"Bearer {access_token['access_token']}")

    def get_current_user(self) -> Optional[Union[str, None]]:
        """Retrieves information about the current user.

        Returns:
            Optional[Union[str, None]]: Current user data if available, otherwise None.
        """
        response = requests.get(self.URL + 'api/me', headers=self.headers)
        return self.parse(response)

    def list_connections(self, page: Optional[int] = None) -> Optional[Union[str, None]]:
        """Retrieves a list of contacts.

        Args:
            page (int, optional): Page number. Defaults to None.

        Returns:
            Optional[Union[str, None]]: Connection list if available, otherwise None.
        """
        url_text = 'api/connections'
        if page:
            url_text += f'?page={page}'
        response = requests.get(self.URL + url_text, headers=self.headers)
        return self.parse(response)

    def parse(self, response: requests.Response) -> Union[str, None]:
        """Parses the HTTP response and handles different status codes.

        Args:
            response (requests.Response): HTTP response.

        Returns:
            Union[str, None]: Parsed data from the response.
        """

        status_code = response.status_code

        if "Content-Type" in response.headers and "application/json" in response.headers["Content-Type"]:
            try:
                r = response.json()
            except ValueError:
                r = response.text
        else:
            r = response.text

        if status_code == 200:
            return r
        if status_code == 204:
            return None
        if status_code == 400:
            raise WrongFormatInputError(r)
        if status_code == 401:
            raise UnauthorizedError(r)
        if status_code == 500:
            raise Exception
        return r
