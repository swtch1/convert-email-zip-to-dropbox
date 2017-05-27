import tempfile

from extract_zipped_email_attachments.settings import auth
from extract_zipped_email_attachments import mail


if __name__ == '__main__':
    imap_session = mail.establish_imap_session()
    for folder in auth['email']['folders_to_search']:
        mail.ensure_mail_folder_exists(imap_session, folder)
        message_ids = mail.get_message_ids(imap_session, folder)
        subjects = mail.build_message_subjects_dict(imap_session, message_ids)
        print(subjects)

    # TODO: do something with this
    with tempfile.TemporaryDirectory() as downloads_dir:
        pass
