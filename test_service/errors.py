from fastapi import HTTPException

no_available_examination = HTTPException(status_code=404, detail="Unable to find available examination")
no_file = HTTPException(status_code=404, detail="Unable to find file")
wrong_file_name = HTTPException(status_code=422, detail="Wrong file name")
already_verified = HTTPException(status_code=409, detail="Already verified")
