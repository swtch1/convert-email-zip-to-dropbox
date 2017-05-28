import tempfile
import os
import re
import zipfile

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
        dest_folder = src_folder + config['reports']['folder_suffix']
        mail.ensure_mail_folder_exists(imap_session, dest_folder)

        src_message_ids = mail.get_message_ids(imap_session, src_folder)
        src_messages_metadata = mail.get_messages_metadata(imap_session, src_message_ids) if src_message_ids != [''] else {}
        dest_message_ids = mail.get_message_ids(imap_session, dest_folder)
        dest_messages_metadata = mail.get_messages_metadata(imap_session, dest_message_ids) if dest_message_ids != [''] else {}

        unique_subjects = get_unique_dict_keys(src_messages_metadata, dest_messages_metadata)

        with tempfile.TemporaryDirectory() as downloads_dir:
            for subject in unique_subjects:
                attachment = mail.download_attachment(imap_session, src_folder, src_messages_metadata[subject]['message_id'], downloads_dir)
                if not re.match(config['reports']['subject_match_regex'], subject.lower()):
                    continue
                if not zipfile.is_zipfile(attachment):
                    continue
                zipped_file = ZippedFile(attachment, password=auth['zip']['password'])
                if zipped_file.zip_invalid:  # TODO: Remove after verification it's not needed anymore.
                    continue
                pdfs = zipped_file.get_pdfs()
                for pdf in pdfs:
                    fully_qualified_pdf = os.path.join(downloads_dir, pdf)
                    zipped_file.extract_file(pdf, downloads_dir)
                    mail.append_message(session=imap_session,
                                        folder=dest_folder,
                                        subject=subject,
                                        to_address=auth['email']['address'],
                                        from_address=auth['email']['reports_from_address'],
                                        attachment=fully_qualified_pdf)
