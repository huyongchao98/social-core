"""
    PAIPASS Oauth2 backend
"""
from .oauth import BaseOAuth2
from ..utils import handle_http_errors
from ..exceptions import AuthCanceled, AuthUnknownError


class PaipassOAuth2(BaseOAuth2):
    """Facebook OAuth2 authentication backend"""
    name = "paipass"
    ID_KEY = "email"
    REDIRECT_STATE = False
    STATE_PARAMETER = False
    ACCESS_TOKEN_METHOD = "POST"
    SCOPE_SEPARATOR = r" "
    AUTHORIZATION_URL = "https://api.demo.p19dev.com/oauth/authorize"
    ACCESS_TOKEN_URL = "https://api.demo.p19dev.com/oauth/token"
    USER_DATA_URL = "https://api.demo.p19dev.com/attributes/paipass/user.data/0"
    EXTRA_DATA = [("expires", "expires"), ]

    def auth_complete_credentials(self):
        return self.get_key_and_secret()

    def get_user_details(self, response):
        """Return user details from Facebook account"""
        email = response.get("email")
        return {"email": email, "username": email.split("@")[0]}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        params = self.setting("PROFILE_EXTRA_PARAMS", {})
        response = kwargs.get('response') or {}
        params["access_token"] = access_token
        headers = {
            "Authorization": "%s %s" % (
                response.get("token_type", "Bearer").capitalize(),
                access_token),
            "Accept": 'application/json',
            "Content-type": 'application/json;charset=utf-8'}
        return self.get_json(self.USER_DATA_URL,
                             params=params, headers=headers)

    @handle_http_errors
    def do_auth(self, access_token, *args, **kwargs):
        """Finish the auth process once the access_token was retrieved"""
        data = self.user_data(access_token, *args, **kwargs)
        response = kwargs.get('response') or {}
        response.update(data or {})
        if 'access_token' not in response:
            response['access_token'] = access_token
        kwargs.update({'response': response, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)
