from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import HTTPException
import jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
pwdContext = CryptContext(schemes=["bcrypt"],deprecated="auto") 

def verifyPassword(plainPassword:str,hashedPassword:str)->bool:
    return pwdContext.verify(plainPassword,hashedPassword)

def hashedPassword(password:str)->str:
    return pwdContext.hash(password)

def createAccessToken(data:dict,expiresDelta: timedelta | None = None):
    toEncode = data.copy()
    if expiresDelta:
        expire = datetime.now(timezone.utc) + expiresDelta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    toEncode.update({"exp":expire})
    encodedJwt = jwt.encode(toEncode,SECRET_KEY,algorithm = ALGORITHM)
    return encodedJwt



