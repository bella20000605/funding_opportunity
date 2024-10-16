import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    # Check if token.json exists for previously authenticated credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use InstalledAppFlow for OAuth login
            flow = InstalledAppFlow.from_client_secrets_file(
                'funding_opportunity/client_secret.json', SCOPES) # This will ensure the script looks for the client_secret.json file inside the funding_opportunity/ folder where your workflow is saving it.
            creds = flow.run_local_server(port=0)  # Use run_console() for non-local environments
        # Save the credentials to token.json for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email(service, sender, recipient, subject, body, attachment_dir):
    # Create the email structure
    message = MIMEMultipart()
    message['to'] = recipient
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(body))

    # Attach files from the attachment directory
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

    # Use environment variables for email addresses
    sender = os.getenv('SENDER_EMAIL', 'js5081@georgetown.edu')  # Use env var or default for local testing
    recipient = os.getenv('RECIPIENT_EMAIL', 'jz922@georgetown.edu')

    subject = 'Test Email with Multiple Attachments'
    body = 'This is a test email with all files in the downloads folder attached.'
    attachment_dir = os.path.join(os.getcwd(), 'downloads')

    send_email(service, sender, recipient, subject, body, attachment_dir)

if __name__ == '__main__':
    main()