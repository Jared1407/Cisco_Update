import requests
import json

url = "https://api.cisco.com/software/v4.0/metadata/pidrelease"

headers = {
    "pid":"ASR10012XOC3POS-RF",
    "currentReleaseVersion": "5.4.3",
    "outputReleaseVersion": "latest"
}



response = requests.request("GET",url, headers=headers)

print(response.json)