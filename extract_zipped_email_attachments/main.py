import tempfile

from extract_zipped_email_attachments.settings import config, auth
from extract_zipped_email_attachments.utilities import get_unique_dict_keys
from extract_zipped_email_attachments import mail

if __name__ == '__main__':
    imap_session = mail.establish_imap_session()
    for src_folder in auth['email']['folders_to_search']:
        dest_folder = src_folder + config['reports_folder_suffix']
        mail.ensure_mail_folder_exists(imap_session, dest_folder)

        src_message_ids = mail.get_message_ids(imap_session, src_folder)
        src_subjects = mail.build_message_subjects_dict(imap_session, src_message_ids) if src_message_ids != [''] else {}
        dest_message_ids = mail.get_message_ids(imap_session, dest_folder)
        dest_subjects = mail.build_message_subjects_dict(imap_session, dest_message_ids) if dest_message_ids != [''] else {}

        unique_subjects = get_unique_dict_keys(src_subjects, dest_subjects)



