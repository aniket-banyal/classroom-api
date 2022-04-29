from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class MyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'drf_social_oauth2.authentication.SocialAuthentication'
    name = 'Google Authentication'
    match_subclasses = True

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix='Bearer',
        )
