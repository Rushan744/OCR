from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import time
from dotenv import load_dotenv
from PIL import Image
import requests
import io
import pyzbar.pyzbar as pyzbar

load_dotenv()

subscription_key = os.environ["SUBSCRIPTION_KEY"]
endpoint = os.environ["ENDPOINT"]
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def extract_text_from_image(image_url):
    # Call API with image URL and raw response (allows you to get the operation location)
    read_response = computervision_client.read(image_url, raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Extract and return all the detected text
    detected_text = ""
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                detected_text += line.text + "\n"
    else:
        print("Failed to extract text from the image.")

    return detected_text

def extract_qr_code(image_url):
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content))
    decoded_objects = pyzbar.decode(img)
    decoded_text = ""
    for obj in decoded_objects:
        decoded_text += obj.data.decode('utf-8') + "\n"
    return decoded_text

image_url = "https://invoiceocrp3.azurewebsites.net/static/FAC_2019_0007-2747871.png"


all_text = extract_text_from_image(image_url)

qr_code_text = extract_qr_code(image_url)

print("Detected Text:")
print(all_text)

print("QR Code Content:")
print(qr_code_text)

print("End of processing.")
