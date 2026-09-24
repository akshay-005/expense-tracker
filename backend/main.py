from fastapi import FastAPI, Form
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_model, load_dotenv
import re
import os

# Load the keys from the local .env file when testing locally
load_dotenv()

app = FastAPI()

# Python safely fetches variables from system environment memory space
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Initialize the authorized Twilio client agent securely
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def parse_bank_sms(sms_text):
    amount_pattern = r"(?:INR|Rs\.?|INR\s|₹)\s*([\d,]+\.\d{2})"
    vendor_pattern = r"(?:at|to|vpa)\s+([A-Za-z0-9\s]+?)(?=\s+on|\s+Ref|\s+A/c|\.|$)"

    amount_match = re.search(amount_pattern, sms_text)
    vendor_match = re.search(vendor_pattern, sms_text, re.IGNORECASE)
    
    amount = amount_match.group(1) if amount_match else None
    vendor = vendor_match.group(1).strip() if vendor_match else "Unknown Vendor"
    
    return amount, vendor

@app.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...)):
    incoming_msg = Body
    
    if any(keyword in incoming_msg.lower() for keyword in ["debited", "spent", "charged", "₹"]):
        amount, vendor = parse_bank_sms(incoming_msg)
        
        if amount:
            reply_text = f"✅ **Expense Logged!**\n💰 Amount: ₹{amount}\n🏪 Vendor: {vendor}\n🏷️ Category: Pending Categorization"
        else:
            reply_text = "I saw a transaction message, but couldn't parse the amount cleanly."
    else:
        reply_text = "👋 Hi! Send me a copy-pasted bank transaction SMS, and I will track it automatically."

    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)
