import os  # for the environment variables
import uuid  # for unique id generation
import re  # For use with regular expressions
import uvicorn
import requests
from fastapi import FastAPI, HTTPException  # pylint: disable=import-error
from subprocess import run
import logging
import json
import sys
import time
import swagger_client
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.ai.textanalytics import TextAnalyticsClient 
from azure.core.credentials import AzureKeyCredential

app = FastAPI()

SUBSCRIPTION_KEY = "9f4badcb741c498a8a5157b41585a821"
SERVICE_REGION = "uksouth"
NAME = "Simple transcription"
DESCRIPTION = "Simple transcription description"
LOCALE = "en-US"
RECORDINGS_CONTAINER_URI = "https://tiamataudioin.blob.core.windows.net/audio?sp=rwl&st=2023-05-10T08:19:57Z&se=2023-05-10T16:19:57Z&spr=https&sv=2022-11-02&sr=c&sig=gCFXtNB15VICccUQNQNmJH4%2BZicF%2FWeEzI1qAr2sk7c%3D"
STORAGE_ACCOUNT = "rg-tiamat"
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=tiamataudioin;AccountKey=+jm1JoRK1S7xnivK38o890h4Qo/AXIqWUzxDAK4P/6CZ54HbJ4gY+I0XKGzpb8Kr2ck9GuTBeh3L+AStO3LRoQ==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = 'audio'
END_POINT = "https://tiamat-cog-services.cognitiveservices.azure.com/"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# configure API key authorization: subscription_key
configuration = swagger_client.Configuration()
configuration.api_key["Ocp-Apim-Subscription-Key"] = SUBSCRIPTION_KEY
configuration.host = f"https://{SERVICE_REGION}.api.cognitive.microsoft.com/speechtotext/v3.1"
logger.info(f"API Key Configuration")

# create the client object and authenticate
client = swagger_client.ApiClient(configuration)
logger.info(f"Client Object Creation and Authentication")

# create an instance of the transcription api class
api = swagger_client.CustomSpeechTranscriptionsApi(api_client=client)

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
            raise Exception(f"could not receive paginated data: status {status}")


@app.get("/")
def read_root():
    """This tells me that the API is working"""
    return {"Hello": "Tiamat have a working API"}

@app.post("/transcribe/start")
def transcribe():
    """This will transcribe all audio files from a specified container"""

    logger.info("Starting transcription client...")
    logger.info(f"Transcription API Class instance")

    properties = swagger_client.TranscriptionProperties()
    transcription_definition = transcribe_from_container(RECORDINGS_CONTAINER_URI, properties)
    logger.info(f"Transcribe from container method run")

    created_transcription, status, headers = api.transcriptions_create_with_http_info(transcription=transcription_definition)

    transcription_id = headers["location"].split("/")[-1]
    logger.info(f"Transaction ID from Location URI")

    logger.info(f"Created new transcription with id: '{transcription_id}' in region {SERVICE_REGION}")
    return (f"Created new transcription with id: {transcription_id} ")

@app.get("/transcribe/status")
def transcription_status(transcription_id: str):
    """Get the transcription job """

    transcription = api.transcriptions_get(transcription_id)
    logger.info(f"Transcriptions status: {transcription.status}")
    return (f"Transcriptions status: {transcription.status}")
    
@app.get("/testing/error")
def transcription_error(transcription_id: str):
    """Check for error message to understand why a transcription job may have failed"""
    transcription = api.transcriptions_get(transcription_id)

    if transcription.status == "Failed":
        error = transcription.properties.error.message
        logger.info(f"Transcriptions status: {error}")
        return (f"Transcriptions status: {error}")
    else:
        return (f"Transcription job successful. No error message to display.")

@app.get("/transcription/file")
def transcription_file(transcription_id: str):
    """Creates the transcription test file"""

    transcription = api.transcriptions_get(transcription_id)
    
    if transcription.status == "Succeeded":
            pag_files = api.transcriptions_list_files(transcription_id)
            for file_data in _paginate(api, pag_files):
                if file_data.kind != "Transcription":
                    continue

                audiofilename = file_data.name
                results_url = file_data.links.content_url
                results = requests.get(results_url)
                logger.info(f"Results for {audiofilename}:\n{results.content.decode('utf-8')}")

                local_transcript = (f"transcription-{transcription_id}.json")

                f = open(local_transcript, "a")
                f.write(results.content.decode('utf-8'))
                f.close

                logger.info("Starting upload")

                blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
                container_client = blob_service_client.get_container_client(CONTAINER_NAME)
                blob_client = container_client.get_blob_client(local_transcript)

                logger.info("Blob client set up")

                with open(local_transcript, "rb") as data:
                    blob_client.upload_blob(data, overwrite = True)
                
                return(f"Transcription: {transcription_id} uploaded to Azure Blob Storage")
    else:
        return ("No successful transcript created for this ID")

@app.get("/transcription/medical") 
def transcription_file(transcription_id: str): 
    """Creates the transcription test file"""

    transcription = api.transcriptions_get(transcription_id)

    local_transcript = (f"transcription-{transcription_id}.json")
    os.remove(local_transcript)

    if transcription.status == "Succeeded":
            pag_files = api.transcriptions_list_files(transcription_id)
            for file_data in _paginate(api, pag_files):
                if file_data.kind != "Transcription":
                    continue

                audiofilename = file_data.name
                results_url = file_data.links.content_url
                results = requests.get(results_url)
                logger.info(
                    f"Results for {audiofilename}:\n{results.content.decode('utf-8')}")
                
                logger.info("Starting upload")

                my_text = requests.get(results_url)
                results_as_text = json.loads(my_text.text)
                blob_text =  results_as_text['combinedRecognizedPhrases'][-1]['lexical']
                logger.info(blob_text)

                logger.info("Starting Text Analytics for Health")
                credential = AzureKeyCredential("c86c64f316a2458a96b14908435e744b")
                text_analytics_client = TextAnalyticsClient(END_POINT, credential)

                response = text_analytics_client.begin_analyze_healthcare_entities([blob_text])
                logger.info("Medical transcription processed")
                result = response.result()
                
                entities_list = []
                docs = [doc for doc in result if not doc.is_error]

                print("Results of Healthcare Entities Analysis:")
                for idx, doc in enumerate(docs):
                    for entity in doc.entities:
                        entities_list.append({'text': entity.text, 'normalized_text': entity.normalized_text})
                        print(f"Entity: {entity.text}")
                        print(f"...Normalized Text: {entity.normalized_text}")

                return entities_list
    else: 
        return ("No successful transcript created for this ID")
