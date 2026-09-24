from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()


@app.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...)):

    print("MESSAGE RECEIVED:", Body)

    resp = MessagingResponse()
    resp.message("✅ Your WhatsApp webhook is working!")

    print("TWIML RESPONSE:", str(resp))

    return Response(
        content=str(resp),
        media_type="application/xml"
    )