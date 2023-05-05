import os  # for the environment variables
import uuid  # for unique id generation
import re  # For use with regular expressions
import requests
from fastapi import FastAPI, HTTPException  # pylint: disable=import-error
import transcribe
from subprocess import run
import logging
import sys
import time
import swagger_client

app = FastAPI()

@app.get("/")
def read_root():
    """This tells me that the API is working"""
    return {"Hello": "Tiamat have a working API"}

@app.post("/transcribe")
def transcribe():  #sub_key:str, region:str, container_uri:str
    """This will transcribe all audio files from a specified container"""

    run('python ./transcribe.py')
    if os.stat("transcription.txt").st_size != 0:
        return{"Success": "Transcription file created"}
    else:
        return{"Failed": "Please try again"}