from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("API Key Found:", api_key is not None)

client = OpenAI(api_key=api_key)

models = client.models.list()

print("Authentication Successful!")