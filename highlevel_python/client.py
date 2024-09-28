import requests
import os
from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session
from typing import Optional, Union, Dict, Any

from highlevel_python.exceptions import UnauthorizedError, WrongFormatInputError


class Client:
    BASE_URL = "https://services.leadconnectorhq.com/"
    AUTH_URL = "https://marketplace.leadconnectorhq.com/oauth/chooselocation"
    TOKEN_URL = "https://services.leadconnectorhq.com/oauth/token"
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.token = None

    @property
    def headers(self) -> Dict[str, str]:
        headers = self.HEADERS.copy()
        if self.token:
            headers["Authorization"] = f"Bearer {self.token['access_token']}"
        return headers

    def authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state,
        }
        return self.AUTH_URL + "?" + urlencode(params)

    def get_access_token(self, code: str) -> Dict[str, Any]:
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }
        response = requests.post(self.TOKEN_URL, headers=self.HEADERS, json=data)

        if response.status_code == 200:
            self.token = response.json()
            return self.token
        else:
            raise UnauthorizedError(f"Error fetching access token: {response.text}")

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        response = requests.post(self.TOKEN_URL, headers=self.HEADERS, json=data)

        if response.status_code == 200:
            self.token = response.json()
            return self.token
        else:
            raise UnauthorizedError(f"Error refreshing access token: {response.text}")

    def set_token(self, token: Dict[str, Any]) -> None:
        self.token = token

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = self.BASE_URL + endpoint
        response = requests.request(method, url, headers=self.headers, json=data)
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Any:
        status_code = response.status_code
        if "application/json" in response.headers.get("Content-Type", ""):
            data = response.json()
        else:
            data = response.text

        if status_code == 200:
            return data
        if status_code == 204:
            return None
        if status_code == 400:
            raise WrongFormatInputError(data)
        if status_code == 401:
            raise UnauthorizedError(data)
        if status_code == 500:
            raise Exception("Internal Server Error")

        return data

    def get_current_user(self) -> Optional[Union[str, None]]:
        return self._request("GET", "api/me")

    def list_connections(self, page: Optional[int] = None) -> Optional[Union[str, None]]:
        endpoint = "api/connections"
        if page:
            endpoint += f"?page={page}"
        return self._request("GET", endpoint)

    def get_contact(self, get_payload: dict, identifier: str, page: Optional[int] = None) -> Optional[Union[str, None]]:
        endpoint = "api/contacts"
        return self._request("GET", endpoint, data=get_payload)

    def create_contact(self, payload: dict) -> Optional[Union[str, None]]:
        endpoint = "api/contacts"
        return self._request("POST", endpoint, data=payload)

    def create_opportunity(self, payload: dict) -> Optional[Union[str, None]]:
        endpoint = "api/opportunities"
        return self._request("POST", endpoint, data=payload)

    def create_task(self, payload: dict, contact_identifier: str) -> Optional[Union[str, None]]:
        contact = self.get_contact(identifier=contact_identifier)
        payload["contact"] = contact
        endpoint = "api/tasks"
        return self._request("POST", endpoint, data=payload)

    def add_contact_to_campaign(self, payload: dict, campaign_id: int) -> Optional[Union[str, None]]:
        payload["campaign_id"] = campaign_id
        endpoint = "api/campaigns"
        return self._request("POST", endpoint, data=payload)
    
    def upload_to_media_library(self, file_path: str) -> Optional[Union[str, None]]:
        endpoint = "medias/upload-file"
        url = self.BASE_URL + endpoint

        # Set up the headers with the Authorization token
        # need form/multipart here, so override the original
        headers = {"Authorization": f"Bearer {self.token['access_token']}"}

        # Prepare the file for upload as multipart form data
        with open(file_path, 'rb') as file:
            files = {
                "file": (os.path.basename(file_path), file)
            }
            # Perform the request to upload the file
            response = requests.post(url, headers=headers, files=files)

        # Handle the response to make sure it's processed correctly
        return self._handle_response(response)
