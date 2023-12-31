import os
import swagger_client
from datetime import datetime, timedelta
from azure.storage.blob import (ContainerSasPermissions, generate_container_sas)

NAME = os.environ.get("NAME")
DESCRIPTION = os.environ.get("DESCRIPTION")
LOCALE = os.environ.get("LOCALE","en-US")


def generate_sas_uri(account_name, account_key, container_name): 

    token = generate_container_sas(
                account_name= str(account_name),
                account_key= str(account_key),
                container_name= str(container_name),
                permission=ContainerSasPermissions(read=True, add=True, create=True, write=True, list=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

    sas_uri = f"https://{account_name}.blob.core.windows.net/{container_name}?{token}"
    return sas_uri

def transcribe_from_container(uri, properties):
    """
    Transcribe all files in the container located at `uri` using the settings specified in `properties`
    using the base model for the specified locale.
    """
    transcription_definition = swagger_client.Transcription(
        display_name=NAME,
        description=DESCRIPTION,
        locale=LOCALE,
        content_container_url=uri,
        properties=properties
    )
    
    return transcription_definition

def _paginate(api, paginated_object):
    """
    The autogenerated client does not support pagination. This function returns a generator over
    all items of the array that the paginated object `paginated_object` is part of.
    """
    yield from paginated_object.values
    typename = type(paginated_object).__name__
    auth_settings = ["api_key"]
    while paginated_object.next_link:
        link = paginated_object.next_link[len(api.api_client.configuration.host):]
        paginated_object, status, headers = api.api_client.call_api(link, "GET",
            response_type=typename, auth_settings=auth_settings)

        if status == 200:
            yield from paginated_object.values
        else:
            raise Exception(f"Could not receive paginated data: status {status}")