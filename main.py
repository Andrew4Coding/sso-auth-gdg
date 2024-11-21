import os
import xml.etree.ElementTree as ET
import urllib.request
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from a .env file (optional)
load_dotenv()

app = FastAPI()

# Load the secret key from environment variable
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables!")


def create_jwt(payload: dict, secret: str, algorithm: str = "HS256"):
    """
    Create a JWT token with the given payload.
    """
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    payload.update({"exp": expiration})  # Add expiration to the payload
    token = jwt.encode(payload, secret, algorithm)
    return token


@app.get("/")
async def root(request: Request, service="", ticket=""):
    current_url = request.url
    
    if not service and not ticket:
        return RedirectResponse(url=f"https://sso.ui.ac.id/cas2/login?service={current_url}")
    
    current_url = str(current_url).split("?")[0]
    fetch_url = f"https://sso.ui.ac.id/cas2/serviceValidate?service={current_url}&ticket={ticket}"
    
    try:
        with urllib.request.urlopen(fetch_url) as response:
            raw_data = response.read().decode("utf-8")
        
        print(f"Raw XML Response: {raw_data}")
        cleaned_xml = raw_data.strip()
        root = ET.fromstring(cleaned_xml)
        namespace = {'cas': 'http://www.yale.edu/tp/cas'}
        
        user = root.find(".//cas:user", namespace).text
        ldap_cn = root.find(".//cas:ldap_cn", namespace).text
        kd_org = root.find(".//cas:kd_org", namespace).text
        role = root.find(".//cas:peran_user", namespace).text
        name = root.find(".//cas:nama", namespace).text
        npm = root.find(".//cas:npm", namespace).text
        
        # Create a payload for JWT
        payload = {
            "user": user,
            "ldap_cn": ldap_cn,
            "organizational_code": kd_org,
            "role": role,
            "name": name,
            "npm": npm
        }
        
        # Encrypt the data with JWT
        token = create_jwt(payload, SECRET_KEY)
        
        return {
            "message": "Data successfully encrypted",
            "jwt_token": token
        }
    except ET.ParseError as e:
        print(f"XML Parsing Error: {e}")
        return {"error": "Failed to parse the XML response", "details": str(e)}
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"error": "An unexpected error occurred", "details": str(e)}
