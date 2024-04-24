from .utils import TokenManager

def GetAccess(refreshToken: str, region: str = "Americas") -> TokenManager:
    """Initiates the TokenManager class using the provided refresh token and region,
    managing the retrieval and refresh of an API access token.

    Parameters
    ----------
    refreshToken : str
        The refresh token used to generate a new access token.

    region : str, optional
        The geographic region to define the URL to be used. Default is "Americas".

    Returns
    -------
    TokenManager
        An instance of TokenManager initialized with the specified refresh token and region.
    """
    return TokenManager(refreshToken, region)