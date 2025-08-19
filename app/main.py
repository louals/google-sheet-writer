from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

app = FastAPI()

# Allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class Appointment(BaseModel):
    fullName: str
    email: str
    phone: str = ""
    company: str = ""
    projectIdea: str = ""
    message: str = ""
    meetingDate: str
    meetingHour: str


@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Server is awake!"}

@app.post("/appointments")
async def create_appointment(appointment: Appointment):
    try:
        values = [[
            appointment.fullName,
            appointment.email,
            appointment.phone,
            appointment.company,
            appointment.projectIdea,
            appointment.meetingDate,
            appointment.meetingHour,
            appointment.message
        ]]
        result = sheet.values().append(
            spreadsheetId=SHEET_ID,
            range="Sheet1!A:H",
            valueInputOption="RAW",
            body={"values": values}
        ).execute()
        return {"success": True, "message": "Appointment added!", "result": result}
    except Exception as e:
        print("Sheets error:", e)   # <--- print actual error
        raise HTTPException(status_code=500, detail="Error writing to Google Sheet")