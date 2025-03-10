import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

BASIC_AUTH_USERNNAME = os.environ['BASIC_AUTH_USERNNAME']
BASIC_AUTH_PASSWORD = os.environ['BASIC_AUTH_PASSWORD']


def Authenticate(credentials: HTTPBasicCredentials = Depends(security)):
  correct_username = secrets.compare_digest(credentials.username, BASIC_AUTH_USERNNAME)
  correct_password = secrets.compare_digest(credentials.password,BASIC_AUTH_PASSWORD)
  if not (correct_username and correct_password):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )
  return True
