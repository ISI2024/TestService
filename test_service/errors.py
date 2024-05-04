from fastapi import HTTPException

no_examination = HTTPException(status_code=404, detail="Unable to find examination with given id")
already_updated = HTTPException(status_code=409, detail="Already verified")

no_user_with_given_login = HTTPException(status_code=404, detail="User with given login not found")
no_money = HTTPException(status_code=409, detail="You don't have enough money!")
credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
qr_code_expired = HTTPException(status_code=401, detail="QR code is invalid or expired")