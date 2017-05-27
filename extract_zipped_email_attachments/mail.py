import imaplib
import email
import re
import os

from extract_zipped_email_attachments.settings import config, auth
from extract_zipped_email_attachments.utilities import convert_bytes_to_string


svdir = 'c:/downloads'

def establish_imap_session():
    session = imaplib.IMAP4_SSL(host=config['imap']['server']['incoming'],
                                port=config['imap']['port']['incoming'])
    typ, account_details = session.login(user=auth['email']['address'],
                                         password=auth['email']['password'])

    if typ != 'OK':
        print('unable to sign in')  # FIXME
        exit(1)

    return session

#######################
imap_session = imaplib.IMAP4_SSL('secure.emailsrvr.com')
imap_session.login('sterling@jlmanagement.net', '#wzs4zuau')
imap_session.select('Inbox/email_testing_remove_after_6_1_17')
# imap_session.select('Inbox/Advance-Monroe')
typ, message_ids = imap_session.search(None, 'ALL')
#######################

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
    subjects = {}
    for i in message_ids:
        subjects[_get_message_subject(session, i)] = i
    return subjects


def get_message_ids(session, folder):
    """
    Get message ids for all messages in an inbox.
    :param session: imap session
    :param folder: inbox to search
    :return: list of message ids, as strings
    """
    session.select(folder)
    typ, message_ids = session.search(None, 'ALL')
    if typ != 'OK':
        print('error searching src_folder')  # FIXME
    return [convert_bytes_to_string(message_id) for message_id in message_ids]


def download_attachment(session, message_id, download_dir):
    typ, message_parts = session.fetch(message_id, '(RFC822)')
    if typ != 'OK':
        print('error fetching mail')  # FIXME

    try:
        email_body = message_parts[0][1]
        mail = email.message_from_string(convert_bytes_to_string(email_body))
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



