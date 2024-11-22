import jwt
from dotenv import load_dotenv
from main import SECRET_KEY

load_dotenv()

with open ("./tokens.txt", "r") as f:
    tokens = f.readlines()
    
for token in tokens:
    try:
        decoded = jwt.decode(token.strip(), SECRET_KEY, algorithms=["HS256"])
        print(decoded, file=open("verified.txt", "w"))
    except jwt.exceptions.DecodeError:
        print("Invalid token")