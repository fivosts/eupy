#!/usr/bin/env python
import os
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime
from time import sleep
import smtplib, ssl, imaplib, email
import subprocess, os
from getpass import getpass, getuser
import socket

class gmail:

  _port = 465
  _smtp_server = "smtp.gmail.com"
  _hostname    = socket.gethostname()
  _cachePath   = "{}/.config/hermes".format(str(Path.home()))
  _cacheFile   = "pass.txt"

  def __init__(self, receiver, cred=[], cache=True):
    
    self._setup(cred, receiver, cache)
    return

  ## Init handler to set up credential and receiver information
  def _setup(self, cred, receiver, cache):

    assert receiver != "", "Receiver mail field is empty"
    cach_creds = self._searchCacheOrUpdate(cred, cache)
    self._username, self._password = cach_creds[0], cach_creds[1]
    self._receiver = receiver
    return

  ## Search cache for existing credentials. If found, check if newer are given
  def _searchCacheOrUpdate(self, cred, cache):
    creds = []
    ## If credentials are found in cache get them
    if os.path.isfile("{}/{}".format(self._cachePath, self._cacheFile)):
      with open("{}/{}".format(self._cachePath, self._cacheFile), 'r') as pf:
        creds = pf.read().splitlines()
        assert len(creds) == 2, "Cached credentials have wrong format!"
        assert creds[0] != "" and creds[1] != "", "Username or password field is empty"
      ## Given credentials are considered fresher than cached
      if len(cred) == 2 and creds != cred:
        creds = cred
        ## Write to cache, if instructed
        if cache:
          self._writeCache(creds)
    ## Otherwise use the given ones, if given
    else:
      # assert len(cred) == 2, "Format of input tuple for username/password is incorrect"
      # assert cred[0] != "" and cred[1] != "", "Username or password field is empty"
      creds.append(input("Sender email username: "))
      creds.append(str(getpass("Password: ")))
      ## Write to cache, if instructed
      if cache:
        self._writeCache(creds)
    return creds

  ## Update mail credentials to cache
  def _writeCache(self, cred):
    if not os.path.isdir(self._cachePath):
      os.makedirs(self._cachePath)
    with open("{}/{}".format(self._cachePath, self._cacheFile), 'w') as pf:
      pf.write("\n".join(cred))
    return

  ## Return username allocated to self object
  def user(self):
    return self._username

  ## Core function to broadcast a message to receiver
  def broadcast(self, reporting_module, msg, request_reply = False):

    if self._password == "":
      assert False, "SMTP Server password for {} not specified!".format(self._username)

    message = self._generate_message(reporting_module, msg)
    self._send_message(message)

    if request_reply:
      self._mailbox_check_wait(message)
      cmd = self._receive_instruction()
      self._execute_instructions(cmd)
      return cmd

    return

  ## MIME message constructor
  def _generate_message(self, rm, m):
    message = MIMEText("---------------------------------------\n{}\n---------------------------------------\n\nReported by mail agent".format(m))
    message['Subject'] = "{}:{}".format(self._hostname, rm)
    message['From'] = self._username
    message['To'] = self._receiver
    message['Sent'] = str(datetime.now())
    return message

  def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}


  def create_message_with_attachment(
      sender, to, subject, message_text, file):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
      content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
      fp = open(file, 'rb')
      msg = MIMEText(fp.read(), _subtype=sub_type)
      fp.close()
    elif main_type == 'image':
      fp = open(file, 'rb')
      msg = MIMEImage(fp.read(), _subtype=sub_type)
      fp.close()
    elif main_type == 'audio':
      fp = open(file, 'rb')
      msg = MIMEAudio(fp.read(), _subtype=sub_type)
      fp.close()
    else:
      fp = open(file, 'rb')
      msg = MIMEBase(main_type, sub_type)
      msg.set_payload(fp.read())
      fp.close()
    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}

  def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print 'Message Id: %s' % message['id']
    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

  ## Login to smtp server using credentials and send message
  def _send_message(self, message):

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(self._smtp_server, self._port, context=context) as server:
      server.login(self._username, self._password)
      server.sendmail(self._username, self._receiver, message.as_string())
    return

  ## Fetch mail, extract the body of the message and parse the instruction given
  def _receive_instruction(self):

    r, d = self._fetch_mail(encoding = "(UID BODY[TEXT])")
    msg = self._extract_email(d).as_string().split('\n')
    command = []

    for line in msg:
      if "$cmd" in line:
        command_str = ":".join(line.split(':')[1:])
        command = [x.split() for x in command_str.split(';') if x]
        break

    assert len(command) != 0, "Command field not extracted successfully!"
    return command

  ## Simple routine to execute in bash the instruction given
  def _execute_instructions(self, cmd):

    for c in cmd:
      proc = subprocess.Popen(c, stdout=subprocess.PIPE)
      out, err = proc.communicate()
      ## Convert to logger
      print(out.decode("utf-8"))
    return

  ## Busy waiting for a reply from a specific recipient
  def _mailbox_check_wait(self, message):

    r, d = self._fetch_mail()
    msg = self._extract_email(d)

    ## TODO add time too
    while not (message['Subject'] in msg['Subject'] and message['To'] in msg['From']):   
      sleep(10)
      r, d = self._fetch_mail()
      msg = self._extract_email(d)
    return

  ## Login to mailbox and fetch the latest email
  def _fetch_mail(self, encoding = "(RFC822)"):

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(self._username, self._password)
    mail.list()

    # Out: list of "folders" aka labels in gmail.
    mail.select("inbox", readonly=True) # connect to inbox.
    result, data = mail.search(None, "ALL")
    id_list = data[0].split() # ids is a space separated string
    latest_email_id = id_list[-1] # get the latest
    result, data = mail.fetch(latest_email_id, encoding) # fetch the email body (RFC822) for the given ID

    return result, data

  ## Extract the core message from raw mail data
  def _extract_email(self, data):

    for response_part in data:
      if isinstance(response_part, tuple):
        return email.message_from_bytes(response_part[1])

    assert False, "Main email cannot be extracted: Wrong format!"

"""
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """#Shows basic usage of the Gmail API.
    #Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])
"""