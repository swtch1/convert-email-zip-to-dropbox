import imaplib
import re
import os
import time
from email import message_from_string, encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

from extract_zipped_email_attachments.utilities import convert_bytes_to_string


def establish_imap_session(host, port, user, password):
    print('creating imap session')  # FIXME
    session = imaplib.IMAP4_SSL(host=host, port=port)
    typ, account_details = session.login(user=user, password=password)

    if typ != 'OK':
        print('unable to sign in')  # FIXME
        exit(1)
    return session


def ensure_mail_folder_exists(session, folder):
    """
    Ensure that a particular src_folder exists.  If it does not, make it.
    :param session: imap session
    :param folder: name of src_folder to check or create
    :return: None
    """
    session.create(folder)


def _get_message_subject(session, message_id):
    """
    Get the message subject for a message, identified by the message id.
    NOTE: This will only return the first subject found.  If there is a chain this may create a bug, but works well for this use case.
    :param message_id: id of the message to get subject for
    :return: message subject
    """
    msg_string = convert_bytes_to_string(session.fetch(str(message_id), '(RFC822)')[1][0][1])
    for msg in msg_string.split('\r\n'):
        if re.match('Subject: .*', msg):
            return re.sub('Subject: ', '', msg)


def build_message_subjects_dict(session, message_ids: list):
    """
    Build a dictionary of src_subjects and message IDs from a message list.
    :param message_ids: 
    :return: dict
    """
    print('building message subjects dictionary')  # FIXME
    subjects = {}
    for i in message_ids[0].split():
        subjects[_get_message_subject(session, i)] = i
    return subjects


def get_message_ids(session, folder):
    """
    Get message ids for all messages in an inbox.
    :param session: imap session
    :param folder: inbox to search
    :return: list of message ids, as strings
    """
    print('getting message ids')  # FIXME
    session.select(folder)
    typ, message_ids = session.search(None, 'ALL')
    if typ != 'OK':
        print('error searching src_folder')  # FIXME
    print('found {} messages in folder {}'.format(len(message_ids[0].split()), folder))  # FIXME
    return [convert_bytes_to_string(message_id) for message_id in message_ids]


def download_attachment(session, folder, message_id, download_dir):
    session.select(folder)
    typ, message_parts = session.fetch(message_id, '(RFC822)')
    if typ != 'OK':
        print('error fetching mail')  # FIXME

    try:
        email_body = message_parts[0][1]
        mail = message_from_string(convert_bytes_to_string(email_body))
        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            file_name = os.path.join(download_dir, part.get_filename())
            with open(file_name, 'wb') as attachment:
                attachment.write(part.get_payload(decode=True))
            return file_name
    except:
        print('error downloading file from message with id {}'.format(message_id))  # FIXME


def append_message(session, folder, subject, to_address, from_address, attachment):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = to_address
    msg['From'] = from_address

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(attachment, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(attachment)))
    msg.attach(part)

    session.append(folder, '', imaplib.Time2Internaldate(time.time()), str(msg).encode())
