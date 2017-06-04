import tempfile
import os

from extract_zipped_email_attachments.settings import config, auth
# from extract_zipped_email_attachments.utilities import get_unique_dict_keys
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

        src_message_ids = mail.get_message_ids(session=imap_session,
                                               folder=src_folder,
                                               search_criteria='(FROM "{}")'.format(auth['email']['recv_reports_from_address']))
        src_messages_metadata = mail.get_messages_metadata(session=imap_session,
                                                           message_ids=src_message_ids) if src_message_ids != [''] else {}
        dest_message_ids = mail.get_message_ids(session=imap_session,
                                                folder=dest_folder)
        dest_messages_metadata = mail.get_messages_metadata(imap_session, dest_message_ids) if dest_message_ids != [''] else {}

        unique_subjects = src_messages_metadata.keys() - dest_messages_metadata.keys()
        sorted_unique_subjects = sorted(unique_subjects, key=lambda x: int(mail.get_message_id_by_subject(x, src_messages_metadata)))

        with tempfile.TemporaryDirectory() as downloads_dir:
            for subject in sorted_unique_subjects:
                message_id = mail.get_message_id_by_subject(subject, src_messages_metadata)
                print('processing id {}'.format(message_id))  # TODO: remove - testing
                attachment = mail.download_attachment(imap_session, src_folder, message_id, downloads_dir)
                zipped_file = ZippedFile(attachment, password=auth['zip']['password'])
                if zipped_file.zip_invalid:
                    continue
                pdfs = zipped_file.get_pdfs()
                for pdf in pdfs:
                    fully_qualified_pdf = os.path.join(downloads_dir, pdf)
                    zipped_file.extract_file(pdf, downloads_dir)
                    mail.append_message(session=imap_session,
                                        folder=dest_folder,
                                        subject=subject,
                                        to_address=auth['email']['address'],
                                        from_address=auth['email']['send_reports_from_address'],
                                        attachment=fully_qualified_pdf)
