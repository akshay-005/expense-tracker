from fastapi import FastAPI, Form
from twilio.twiml.messaging_response import MessagingResponse
import re

app = FastAPI()

def parse_bank_sms(sms_text):
    # Extracts amounts like ₹450.00, Rs. 500, INR 1000
    amount_pattern = r"(?:INR|Rs\.?|INR\s|₹)\s*([\d,]+\.\d{2})"
    vendor_pattern = r"(?:at|to|vpa)\s+([A-Za-z0-9\s]+?)(?=\s+on|\s+Ref|\s+A/c|\.|$)"

    amount_match = re.search(amount_pattern, sms_text)
    vendor_match = re.search(vendor_pattern, sms_text, re.IGNORECASE)
    
    amount = amount_match.group(1) if amount_match else None
    vendor = vendor_match.group(1).strip() if vendor_match else "Unknown Vendor"
    
    return amount, vendor

@app.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...)):
    """This function triggers every time a WhatsApp message hits our backend"""
    incoming_msg = Body
    
    # Check if the incoming message looks like a bank transaction
    if any(keyword in incoming_msg.lower() for keyword in ["debited", "spent", "charged", "₹"]):
        amount, vendor = parse_bank_sms(incoming_msg)
        
        if amount:
            reply_text = f"✅ **Expense Logged!**\n💰 Amount: ₹{amount}\n🏪 Vendor: {vendor}\n🏷️ Category: Pending Categorization"
        else:
            reply_text = "I saw a transaction message, but couldn't parse the amount cleanly. Please enter manually."
    else:
        reply_text = "👋 Hi! Send me a copy-pasted bank transaction SMS, and I will track it automatically."

    # Format the response using Twilio's XML standard (TwiML)
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)
