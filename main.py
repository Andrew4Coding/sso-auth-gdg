import json
import os
import xml.etree.ElementTree as ET
import urllib.request
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import jwt
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# Load the secret key from environment variable
SECRET_KEY = os.getenv("SECRET_KEY") 


# Open Json
with open ("parsed.json", "r") as file:
    faculty_data = json.load(file)
    

@app.get("/")
async def root(request: Request, service="", ticket=""):

    current_url = request.url
    
    if not service and not ticket:
        return RedirectResponse(url=f"https://sso.ui.ac.id/cas2/login?service={current_url}")
    
    current_url = str(current_url).split("?")[0]
    fetch_url = f"https://sso.ui.ac.id/cas2/serviceValidate?service={current_url}&ticket={ticket}"
    
    try:
        print("Fetching URL:", fetch_url)  # Debugging line to check the fetch URL
        with urllib.request.urlopen(fetch_url) as response:
            raw_data = response.read().decode("utf-8")

        print("Raw XML Data:", raw_data)  # Debugging line to check the raw XML data
        
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

        print("Parsed User Data:", payload)  # Debugging line to check parsed user data
        
        
        # Get Json Data based on organizational code
        user_faculty_data = [faculty for faculty in faculty_data if faculty["id"] == kd_org][0]
        
        # Encrypt the data with JWT
        token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256')
        
        name = name.replace(" ", "+")
        npm_prefix = npm[:2]
        
        faculty = (user_faculty_data["fakultas"]).replace(" ", "+")
        major = user_faculty_data["prodi"].replace(" ", "+")
        
        if (npm_prefix == "23"):
            batch = "2023"
        elif (npm_prefix == "24"):
            batch = "2024"
        elif (npm_prefix == "25"):
            batch = "2025"

        form_link = f"https://docs.google.com/forms/d/e/1FAIpQLSdpNXKvzx0HnAXdXuGl_IZ2IT9f9oAUZZkcHkycWAGWQxGkfQ/viewform?usp=pp_url&entry.192350530={token}&entry.576572448={name}&entry.1125842942={user}@ui.ac.id&entry.726563284={'Fakultas+' + faculty}&entry.611891497={major}&entry.201197880={batch}"
        
        return RedirectResponse(url=form_link)
        
    except ET.ParseError as e:
        print(f"XML Parsing Error: {e}")
        return {"error": "Failed to parse the XML response", "details": str(e)}
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"error": "An unexpected error occurred", "details": str(e)}

@app.get("/validate")
async def validate(request: Request, token=""):
    try:
        if not token:
            return {"error": "Token is not valid"}
        
        decoded = jwt.decode(token.strip(), SECRET_KEY, algorithms=["HS256"])
        
        csv = ",".join([f"{value}" for key, value in decoded.items()])
        
        return csv
    except:
        return "Token is Not Valid"
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)