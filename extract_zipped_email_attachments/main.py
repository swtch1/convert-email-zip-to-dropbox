from extract_zipped_email_attachments.temp_dir import make_temp_download_dir
from extract_zipped_email_attachments.settings import auth
from extract_zipped_email_attachments import mail


if __name__ == '__main__':
    make_temp_download_dir()
    imap_session = mail.establish_imap_session()
    for folder in auth['email']['folders_to_search']:
        mail.ensure_folder_exists(imap_session, folder)
        message_ids = mail.get_message_ids(imap_session, folder)
        subjects = mail.build_message_subjects_dict(imap_session, message_ids)
        print(subjects)

