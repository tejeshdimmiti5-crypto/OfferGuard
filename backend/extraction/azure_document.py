import base64
import json
import os
import time
import urllib.request

API_VERSION = os.getenv("AZURE_DOCINTEL_API_VERSION", "2024-11-30")

def read_document(data: bytes, content_type: str, timeout_seconds: int = 60) -> str:
    endpoint = os.environ["AZURE_DOCINTEL_ENDPOINT"].rstrip("/")
    key = os.environ["AZURE_DOCINTEL_KEY"]
    url = f"{endpoint}/documentintelligence/documentModels/prebuilt-read:analyze?api-version={API_VERSION}"
    body = json.dumps({"base64Source": base64.b64encode(data).decode("ascii")}).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        operation = response.headers.get("Operation-Location")
    if not operation:
        raise RuntimeError("Document Intelligence did not return an operation location")
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        poll = urllib.request.Request(operation, headers={"Ocp-Apim-Subscription-Key": key})
        with urllib.request.urlopen(poll, timeout=30) as response:
            result = json.load(response)
        status = result.get("status")
        if status == "succeeded":
            return result.get("analyzeResult", {}).get("content", "")
        if status == "failed":
            raise RuntimeError("Document Intelligence could not read the file")
        time.sleep(1.5)
    raise TimeoutError("Document Intelligence timed out")
