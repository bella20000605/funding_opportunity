import os
import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# SCOPES for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    # Load service account credentials from the GitHub secret
    service_account_info = os.environ.get("SERVICE_ACCOUNT_KEY")
    
    # Parse the service account info
    credentials = Credentials.from_service_account_info(eval(service_account_info), scopes=SCOPES)
    
    return credentials

def send_email(service, sender, recipient, subject, body, attachment_dir):
    message = MIMEMultipart()
    message['to'] = recipient
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(body))

    if os.path.exists(attachment_dir):
        files = os.listdir(attachment_dir)
        if not files:
            print(f"No attachments found in {attachment_dir}.")
        for filename in files:
            file_path = os.path.join(attachment_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                    message.attach(part)
    else:
        print(f"Attachment directory {attachment_dir} not found.")

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        sent_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Message sent successfully! Message Id: {sent_message['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")

def main():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    sender = os.getenv('SENDER_EMAIL', 'js5081@georgetown.edu')
    recipient = os.getenv('RECIPIENT_EMAIL', 'jz922@georgetown.edu')
    subject = 'Test Email with Multiple Attachments'
    body = 'This is a test email with all files in the downloads folder attached.'
    attachment_dir = os.path.join(os.getcwd(), 'downloads')

    send_email(service, sender, recipient, subject, body, attachment_dir)

if __name__ == '__main__':
    main()
