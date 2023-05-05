import os  # for the environment variables
import uuid  # for unique id generation
import re  # For use with regular expressions
import requests
from fastapi import FastAPI, HTTPException  # pylint: disable=import-error

app = FastAPI()