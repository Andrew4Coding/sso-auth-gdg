import jwt

with open ("./tokens.txt", "r") as f:
    tokens = f.readlines()
    
for token in tokens:
    try:
        decoded = jwt.decode(token.strip(), "hehe", algorithms=["HS256"])
        print(decoded)
    except jwt.exceptions.DecodeError:
        print("Invalid token")