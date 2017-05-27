import tempfile
import os

from extract_zipped_email_attachments.settings import config, auth
from extract_zipped_email_attachments.utilities import get_unique_dict_keys
from extract_zipped_email_attachments.zip import ZippedFile
from extract_zipped_email_attachments import mail

if __name__ == '__main__':
    imap_session = mail.establish_imap_session(host=config['imap']['server']['incoming'],
                                               port=config['imap']['port']['incoming'],
                                               user=auth['email']['address'],
                                               password=auth['email']['password'])
    for src_folder in auth['email']['folders_to_search']:
        dest_folder = src_folder + config['reports_folder_suffix']
        mail.ensure_mail_folder_exists(imap_session, dest_folder)

        src_message_ids = mail.get_message_ids(imap_session, src_folder)
        src_subjects = mail.build_message_subjects_dict(imap_session, src_message_ids) if src_message_ids != [''] else {}
        dest_message_ids = mail.get_message_ids(imap_session, dest_folder)
        dest_subjects = mail.build_message_subjects_dict(imap_session, dest_message_ids) if dest_message_ids != [''] else {}

        unique_subjects = get_unique_dict_keys(src_subjects, dest_subjects)

        # with tempfile.TemporaryDirectory() as downloads_dir:
        #     for subject in unique_subjects:
        #           stuff here
        #     os.removedirs(downloads_dir)

        downloads_dir = 'c:/Temp/'
        for subject in unique_subjects:
            attachment = mail.download_attachment(imap_session, src_folder, src_subjects[subject], downloads_dir)
            zipped_file = ZippedFile(attachment, password=auth['zip']['password'])
            pdfs = zipped_file.get_pdfs()
            for pdf in pdfs:
                zipped_file.extract_file(pdf, downloads_dir)
