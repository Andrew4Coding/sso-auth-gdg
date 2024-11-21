import urllib.parse
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/")
async def root(request: Request, service="", ticket=""):
    current_url = request.url
    
    print(current_url)
    
    if service == "" and ticket == "":
        # Redirect to
        return RedirectResponse(url=f"https://sso.ui.ac.id/cas2/login?service={current_url}")
    
    current_url = str(current_url).split("?")[0]
    
    # Fetch the ticket
    fetch_url = f"https://sso.ui.ac.id/cas2/serviceValidate?service={current_url}&ticket={ticket}"
    
    fetch_url = urllib.parse.quote(fetch_url, safe='')
    
    response = requests.get(fetch_url)
    
    print(response.url)
    print(response.text)
            
    return {"message": "Hello World", "status": response.status_code, "fetch_url": fetch_url, "response": response.text}