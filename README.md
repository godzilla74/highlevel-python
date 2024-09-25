
# highlevel-python
![](https://img.shields.io/badge/version-0.1.3-success) ![](https://img.shields.io/badge/Python-3.8%20|%203.9%20|%203.10%20|%203.11-4B8BBE?logo=python&logoColor=white)  

*highlevel-python* is an API wrapper for highlevel, written in Python.  
This library uses Oauth2 for authentication.
## Installing
```
pip install git+https://github.com/godzilla74/highlevel-python.git
```
### Usage
```python
from highlevel.client import Client
client = Client(client_id, client_secret, redirect_uri=redirect_uri)
```
To obtain and set an access token, follow this instructions:

1. **Get authorization URL**
```python
url = client.authorization_url(state=None)
# This call generates the url necessary to display the pop-up window to perform oauth authentication
# param state(code) is required for direct request for oauth, for local test isn't necessary
```
2. **Get access token using code**
```python
token = client.get_access_token(code)
# "code" is the same response code after login with oauth with the above url.
```

3. **Refresh access token using refresh_token**
```python
token = client.refresh_access_token(refresh_token)
# "refresh_token" is the token refresh in response after login with oauth with the above url.
```

### Postman Collection

You can find a Postman Collection with API routes and responses in:

https://interstellar-desert-735390.postman.co/workspace/My-Workspace~0f763140-1ebb-48f5-8410-120620bf6c0c/collection/30746140-04303b39-b1da-42de-aee2-5ac4ffbda658?action=share&creator=30746140&active-environment=30746140-00ac4392-b9f1-4d92-86d7-710ce7a58ca6
