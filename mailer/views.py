from django.shortcuts import render, redirect
from allauth.socialaccount.models import SocialToken
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv
import os

import base64
from email.mime.text import MIMEText

load_dotenv()

def home(request):
    return render(request, "home.html")

def send_email_view(request):
    if request.method == "POST":
        user = request.user

        token = SocialToken.objects.filter(account__user=user).first()

        if not token:
            return redirect("/")

        try:
            creds = Credentials(
                token=None,
                refresh_token=token.token_secret,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLOUD_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLOUD_CLIENT_SECRET"),
            )

            creds.refresh(Request())

            service = build("gmail", "v1", credentials=creds)

            to_email = request.POST.get("to")
            subject = request.POST.get("subject")
            body = request.POST.get("body")

            message = MIMEText(body)
            message["to"] = to_email
            message["subject"] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()

        except Exception as e:
            print("❌ ERROR:", str(e))

    return redirect("/")