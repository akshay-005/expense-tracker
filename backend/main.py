from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import re

app = FastAPI()


def parse_bank_sms(sms_text):

    # Extract amount
    amount_pattern = r"₹\s*([\d,]+(?:\.\d{2})?)"

    # Extract vendor after "at"
    vendor_pattern = r"\bat\s+([A-Za-z0-9 &._-]+?)(?=\s+on\b|$)"

    amount_match = re.search(amount_pattern, sms_text)
    vendor_match = re.search(
        vendor_pattern,
        sms_text,
        re.IGNORECASE
    )

    amount = amount_match.group(1) if amount_match else None
    vendor = (
        vendor_match.group(1).strip()
        if vendor_match
        else "Unknown Vendor"
    )

    return amount, vendor


@app.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...)):

    print("MESSAGE RECEIVED:", Body)

    incoming_msg = Body

    # Check whether this looks like a transaction
    if any(
        keyword in incoming_msg.lower()
        for keyword in ["debited", "spent", "charged", "₹"]
    ):

        amount, vendor = parse_bank_sms(incoming_msg)

        if amount:

            reply_text = (
                f"✅ Expense Logged!\n\n"
                f"💰 Amount: ₹{amount}\n"
                f"🏪 Vendor: {vendor}\n"
                f"🏷️ Category: Pending Categorization"
            )

        else:

            reply_text = (
                "⚠️ I detected a transaction, "
                "but couldn't identify the amount."
            )

    else:

        reply_text = (
            "👋 Hi!\n\n"
            "Send me a bank transaction SMS and "
            "I'll track the expense automatically."
        )

    print("REPLY:", reply_text)

    resp = MessagingResponse()
    resp.message(reply_text)

    print("TWIML RESPONSE:", str(resp))

    return Response(
        content=str(resp),
        media_type="application/xml"
    )