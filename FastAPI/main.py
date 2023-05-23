import os
import uvicorn
import requests
import logging
import json
import swagger_client
from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient
from azure.ai.textanalytics import TextAnalyticsClient 
from azure.core.credentials import AzureKeyCredential
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
from utlis import generate_sas_uri, _paginate, transcribe_from_container
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Create FastAPI app 
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialise OTEL
provider = TracerProvider()
# Set the global default tracer provider
trace.set_tracer_provider(provider)
# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)
# Done initialising OTEL

# Get all required Env Variables:
NAME = os.environ.get("NAME")
DESCRIPTION = os.environ.get("DESCRIPTION")
LOCALE = os.environ.get("LOCALE","en-US")
SUBSCRIPTION_KEY = os.environ.get("SUBSCRIPTION_KEY")
SERVICE_REGION = os.environ.get("SERVICE_REGION")
STORAGE_ACCOUNT = os.environ.get("STORAGE_ACCOUNT")
STORAGE_ACCOUNT_KEY = os.environ.get("STORAGE_ACCOUNT_KEY")
CONNECTION_STRING = os.environ.get("CONNECTION_STRING")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME")
HEALTH_ANALYTICS_KEY = os.environ.get("HEALTH_ANALYTICS_KEY")
END_POINT = os.environ.get("END_POINT")

# Log the variables
logging.info(f"NAME: {NAME}")
logging.info(f"DESCRIPTION: {DESCRIPTION}")
logging.info(f"LOCALE: {LOCALE}")
logging.info(f"SUBSCRIPTION_KEY: {SUBSCRIPTION_KEY}")
logging.info(f"SERVICE_REGION: {SERVICE_REGION}")
logging.info(f"STORAGE_ACCOUNT: {STORAGE_ACCOUNT}")
logging.info(f"STORAGE_ACCOUNT_KEY: {STORAGE_ACCOUNT_KEY}")
logging.info(f"CONNECTION_STRING: {CONNECTION_STRING}")
logging.info(f"CONTAINER_NAME: {CONTAINER_NAME}")
logging.info(f"HEALTH_ANALYTICS_KEY: {HEALTH_ANALYTICS_KEY}")
logging.info(f"END_POINT: {END_POINT}")

# Configure API key authorization: subscription_key
configuration = swagger_client.Configuration()
configuration.api_key["Ocp-Apim-Subscription-Key"] = SUBSCRIPTION_KEY
configuration.host = f"https://{SERVICE_REGION}.api.cognitive.microsoft.com/speechtotext/v3.1"
logger.info(f"API Key Authorized")

# Create client object and authenticate
client = swagger_client.ApiClient(configuration)
logger.info(f"Client Object Creation and Authentication")

# Create an instance of the transcription api class
api = swagger_client.CustomSpeechTranscriptionsApi(api_client=client)

# # Prometheus custom metrics
# audio_files_processed = Counter(
#     "audio_files_processed", "Number of processed audio files"
# )

# processing_time = Histogram(
#     "processing_time_seconds",
#     "Time taken to process an audio file (seconds)",
#     buckets=[1, 2, 5, 10, 20, 30, 60, 120, 300, float("inf")],
# )

# concurrent_requests = Gauge(
#     "concurrent_requests", "Number of concurrent requests"
# )

@app.get("/")
def root():
    """This tells me that the API is working"""
    return {"Hello": "Chase, I have a working API"}

@app.post("/transcribe/start")
def transcribe():
    """This will transcribe all audio files from a specified container"""

    logger.info("Starting transcription client...")
    properties = swagger_client.TranscriptionProperties()
    logger.info(f"Transcription API Class instance created")
    

    sas_uri = generate_sas_uri(STORAGE_ACCOUNT, STORAGE_ACCOUNT_KEY, CONTAINER_NAME)
    transcription_definition = transcribe_from_container(sas_uri, properties)
    logger.info(f"Transcribe from container method run")

    created_transcription, status, headers = api.transcriptions_create_with_http_info(transcription_definition)

    transcription_id = headers["location"].split("/")[-1]
    logger.info(f"Transaction ID from Location URI recieved")

    logger.info(f"Created new transcription with id: '{transcription_id}' in region {SERVICE_REGION}")
    return (f" Created new transcription with id: {transcription_id} ")

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

                transcript_name = file_data.name
                results_url = file_data.links.content_url
                results = requests.get(results_url)

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
    with tracer.start_as_current_span("Get transcription ID"):
        transcription = api.transcriptions_get(transcription_id)

        local_transcript = (f"transcription-{transcription_id}.json")
        os.remove(local_transcript)

    if transcription.status == "Succeeded":
        with tracer.start_as_current_span("Extract Transcription Pages"):
            pag_files = api.transcriptions_list_files(transcription_id)
            for file_data in _paginate(api, pag_files):
                if file_data.kind != "Transcription":
                    continue

                results_url = file_data.links.content_url
                
                logger.info("Starting upload")

                my_text = requests.get(results_url)
                results_as_text = json.loads(my_text.text)
                blob_text =  results_as_text['combinedRecognizedPhrases'][-1]['lexical']
                logger.info(blob_text)

                logger.info("Starting Text Analytics for Health")
                credential = AzureKeyCredential(HEALTH_ANALYTICS_KEY)
                text_analytics_client = TextAnalyticsClient(END_POINT, credential)

                with tracer.start_as_current_span("text_analytics_processing"):
                    response = text_analytics_client.begin_analyze_healthcare_entities([blob_text])
                    logger.info("Medical transcription processed")
                    result = response.result()
                    
                    entities_list = []
                    docs = [doc for doc in result if not doc.is_error]

                with tracer.start_as_current_span("Result formatting"):
                    for idx, doc in enumerate(docs):
                        for entity in doc.entities:
                            entities_list.append({'text': entity.text, 'normalized_text': entity.normalized_text})
                            print(f"Entity: {entity.text}")
                            print(f"...Normalized Text: {entity.normalized_text}")
                    return ("Results of Healthcare Entities Analysis:", entities_list)
            else: 
                return ("No successful transcript created for this ID")
