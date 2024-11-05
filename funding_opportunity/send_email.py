# import os
# import json
# import base64
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders

# # If modifying these SCOPES, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# def authenticate_gmail():
#     creds = None
    
#     # Check if token.json exists for previously authenticated credentials
#     if os.path.exists('funding_opportunity/token.json'):
#         creds = Credentials.from_authorized_user_file('funding_opportunity/token.json', SCOPES)
#         print("Using token.json for credentials.")
#     elif os.path.exists('funding_opportunity/client_secret.json'):
#         # If token.json is not found, use client_secret.json to generate new token
#         flow = InstalledAppFlow.from_client_secrets_file('funding_opportunity/client_secret.json', SCOPES)
#         creds = flow.run_local_server(port=0)
#         # Save the credentials to token.json for future use
#         with open('funding_opportunity/token.json', 'w') as token_file:
#             token_file.write(creds.to_json())
#         print("Generated new token.json and saved it.")
#     else:
#         print("Error: client_secret.json not found.")
    
#     # If credentials are expired, refresh them
#     if creds and creds.expired and creds.refresh_token:
#         creds.refresh(Request())
#         with open('funding_opportunity/token.json', 'w') as token_file:
#             token_file.write(creds.to_json())
#         print("Token refreshed.")

#     return creds


# def track_new_files(attachment_dir):
#     """Check for new files in the attachment directory and return only new files."""
#     manifest_file = 'sent_files.txt'  # A file to track sent files
    
#     # Get a list of all CSV files in the attachment directory
#     all_files = [f for f in os.listdir(attachment_dir) if f.endswith('.csv')]
    
#     # Read the list of files that have already been sent
#     if os.path.exists(manifest_file):
#         with open(manifest_file, 'r') as mf:
#             sent_files = set(mf.read().splitlines())
#     else:
#         sent_files = set()

#     # Find new files that haven't been sent yet
#     new_files = [f for f in all_files if f not in sent_files]

#     # Update the manifest file with newly sent files
#     if new_files:
#         with open(manifest_file, 'a') as mf:
#             for new_file in new_files:
#                 mf.write(f"{new_file}\n")

#     return new_files


# def send_email(service, sender, recipient, subject, body, attachment_dir, new_files):
#     # Create the email structure
#     message = MIMEMultipart()
#     message['to'] = recipient
#     message['from'] = sender
#     message['subject'] = subject
#     message.attach(MIMEText(body))

#     # Attach only new files
#     if new_files:
#         for filename in new_files:
#             file_path = os.path.join(attachment_dir, filename)
#             if os.path.isfile(file_path):
#                 with open(file_path, "rb") as attachment:
#                     part = MIMEBase('application', 'octet-stream')
#                     part.set_payload(attachment.read())
#                     encoders.encode_base64(part)
#                     part.add_header('Content-Disposition', f"attachment; filename= {filename}")
#                     message.attach(part)
#     else:
#         print("No new files to attach.")

#     raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

#     try:
#         sent_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
#         print(f"Message sent successfully! Message Id: {sent_message['id']}")
#     except HttpError as error:
#         print(f"An error occurred: {error}")


# def main():
#     creds = authenticate_gmail()
#     service = build('gmail', 'v1', credentials=creds)

#     # Use environment variables for email addresses
#     sender = os.getenv('SENDER_EMAIL', 'js5081@georgetown.edu')  # Use env var or default for local testing
#     recipient = os.getenv('RECIPIENT_EMAIL', 'jz922@georgetown.edu')

#     subject = 'Weekly funding oppoutunities Available'
#     body = 'This is an automated email with newly scraped funding opportunities files attached.'
#     attachment_dir = os.path.join(os.getcwd(), 'downloads_website')

#     # Track new files
#     new_files = track_new_files(attachment_dir)

#     if new_files:
#         send_email(service, sender, recipient, subject, body, attachment_dir, new_files)
#         # Clear sent_files.txt to treat files as new next time
#         open('sent_files.txt', 'w').close()
#     else:
#         print("No new files to send.")

# if __name__ == '__main__':
#     main()

import os
import json
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
    if os.path.exists('funding_opportunity/token.json'):
        creds = Credentials.from_authorized_user_file('funding_opportunity/token.json', SCOPES)
        print("Using token.json for credentials.")
    elif os.path.exists('funding_opportunity/client_secret.json'):
        # If token.json is not found, use client_secret.json to generate new token
        flow = InstalledAppFlow.from_client_secrets_file('funding_opportunity/client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials to token.json for future use
        with open('funding_opportunity/token.json', 'w') as token_file:
            token_file.write(creds.to_json())
        print("Generated new token.json and saved it.")
    else:
        print("Error: client_secret.json not found.")
    
    # If credentials are expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('funding_opportunity/token.json', 'w') as token_file:
            token_file.write(creds.to_json())
        print("Token refreshed.")

    return creds


def send_email(service, sender, recipient, subject, body, attachment_dir):
    # Create the email structure
    message = MIMEMultipart()
    message['to'] = recipient
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(body))

    # Attach all CSV files in the specified directory
    for filename in os.listdir(attachment_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(attachment_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                    message.attach(part)

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

    subject = 'Weekly funding opportunities Available'
    body = 'This is an automated email with all scraped funding opportunities files attached.'
    attachment_dir = os.path.join(os.getcwd(), 'downloads_website')

    # Send email with all files in the directory
    send_email(service, sender, recipient, subject, body, attachment_dir)


if __name__ == '__main__':
    main()
