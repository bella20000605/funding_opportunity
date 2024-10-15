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

# Step 1: Authenticate using OAuth2
def authenticate_gmail():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    # and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './client_secret.json', SCOPES)  # Adjust the path if needed
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Step 2: Send an email using the Gmail API with multiple attachments
def send_email(service, sender, recipient, subject, body, attachment_dir):
    # Create the email
    message = MIMEMultipart()
    message['to'] = recipient
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(body)
    message.attach(msg)

    # Attach all files in the specified directory
    if os.path.exists(attachment_dir):
        for filename in os.listdir(attachment_dir):
            file_path = os.path.join(attachment_dir, filename)
            if os.path.isfile(file_path):  # Only attach files, ignore directories
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                    message.attach(part)
    else:
        print(f"Attachment directory {attachment_dir} not found.")

    # Encode the message in base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        # Send the email using the Gmail API
        sent_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Message sent successfully! Message Id: {sent_message['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")

# Main script
def main():
    creds = authenticate_gmail()

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)

    # Email content
    sender = 'js5081@georgetown.edu'  # Replace with your email
    recipient = 'jz922@georgetown.edu'  # Replace with recipient email
    subject = 'Test Email with Multiple Attachments'
    body = 'This is a test email with all files in the downloads folder attached.'

    # Path to the directory where your CSV files are located (downloads folder)
    attachment_dir = os.path.join(os.getcwd(), './downloads') 

    # Send the email with attachments
    send_email(service, sender, recipient, subject, body, attachment_dir)

if __name__ == '__main__':
    main()
