import imaplib
import re
import os
import time
from email import message_from_string, encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase


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
    typ, message_parts = session.fetch(message_id, '(BODY.PEEK[HEADER])')
    if typ == 'OK':
        msg = message_from_string(message_parts[0][1].decode())
        return msg['subject'].replace('\r\n', '')
    else:
        raise ValueError('error fetching message with id {}'.format(message_id))


def get_messages_metadata(session, message_ids: list):
    """
    Build a dictionary of src_messages_metadata and message IDs from a message list.
    :param message_ids: list of message ids to process
    :return: dict
    """
    # TODO: This is too complex.. make this a class.
    print('building message metadata dictionary')  # FIXME
    metadata = {}
    for message_id in message_ids:
        msg_string = session.fetch(str(message_id), '(RFC822)')[1][0][1].decode()
        split_msg = msg_string.split('\r\n')
        for part in split_msg:
            if re.match('^Subject: .*', part):
                subject = re.sub('Subject: ', '', part)
                break
        metadata[subject] = {}
        metadata[subject]['message_id'] = message_id
        for part in split_msg:
            date_regex = '[0-9]{1,2}\s[A-Z]{1}[a-z]{2}\s[1,2][9,0]\d{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}'
            if re.match('^Date: .*{}\s.*'.format(date_regex), part):
                metadata[subject]['date'] = re.search(date_regex, part).group()
    return metadata


def get_message_ids(session, folder, search_criteria='ALL'):
    """
    Get message ids for all messages in an inbox.
    :param session: imap session
    :param folder: inbox to search
    :return: list of message ids, as strings
    """
    print('getting message ids')  # FIXME
    session.select(folder, readonly=True)
    typ, message_ids = session.search(None, 'ALL')
    if typ != 'OK':
        print('error searching src_folder')  # FIXME
    print('found {} messages in folder {}'.format(len(message_ids[0].split()), folder))  # FIXME
    return [message_id.decode() for message_id in message_ids][0].split()


def download_attachment(session, folder, message_id, download_dir):
    """
    Donwnload an attachment from an email, by message id
    :param session: imap session
    :param folder: inbox to search
    :param message_id: id of message to download attachment from
    :param download_dir: target directory to save attachment to
    :return: str: path of downloaded attachment
    """
    print('downloading attachment for message id {}'.format(message_id))
    session.select(folder, readonly=True)
    typ, message_parts = session.fetch(message_id, '(RFC822)')
    if typ != 'OK':
        print('error fetching mail')  # FIXME

    try:
        msg = message_from_string(message_parts[0][1].decode())
        for part in msg.walk():
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
    print('appending attachment with subject {} to folder {}'.format(subject, folder))
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
