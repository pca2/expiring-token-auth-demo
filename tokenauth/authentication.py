import datetime
from django.utils.timezone import utc
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):

        try:
            token = self.get_model().objects.get(key=key)
        except self.get_model().DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted")

        utc_now = datetime.datetime.now(datetime.timezone.utc)

        if token.created < utc_now - datetime.timedelta(days=30):
            # if token is more than 30 days old, it is expired
            raise exceptions.AuthenticationFailed("Token has expired")

        return (token.user, token)
