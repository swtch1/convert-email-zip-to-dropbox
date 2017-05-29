import tempfile
import os
import time
import threading
import queue
import imaplib

from extract_zipped_email_attachments.settings import config, auth
from extract_zipped_email_attachments.utilities import get_unique_dict_keys
from extract_zipped_email_attachments.zip import ZippedFile
from extract_zipped_email_attachments import mail

src_metadata_queue = queue.Queue()
dest_metadata_queue = queue.Queue()
imap_session = None
src_messages_metadata = None
dest_messages_metadata = None


def build_metadata(queue, session, folder, search_criteria):
    message_ids = mail.get_message_ids(session=session,
                                       folder=folder,
                                       search_criteria=search_criteria)
    metadata = mail.get_messages_metadata(session=session,
                                          message_ids=message_ids)
    ret = metadata if message_ids != [''] else {}
    if config['threading_enabled']:
        queue.put(ret)
    else:
        return ret


if __name__ == '__main__':
    while True:
        try:
            imap_session.noop()
        except (AttributeError, imaplib.IMAP4.abort):
            imap_session = mail.establish_imap_session(host=config['imap']['server']['incoming'],
                                                       port=config['imap']['port']['incoming'],
                                                       user=auth['email']['address'],
                                                       password=auth['email']['password'])

        for src_folder in auth['email']['folders_to_search']:
            dest_folder = src_folder + config['reports']['folder_suffix']
            mail.ensure_mail_folder_exists(imap_session, dest_folder)

            # src_message_ids = mail.get_message_ids(session=imap_session,
            #                                        folder=src_folder,
            #                                        search_criteria='(FROM "{}")'.format(auth['email']['recv_reports_from_address']))
            # src_messages_metadata = mail.get_messages_metadata(session=imap_session,
            #                                                    message_ids=src_message_ids) if src_message_ids != [''] else {}
            if config['threading_enabled']:
                while not src_metadata_queue.empty():
                    src_messages_metadata = src_metadata_queue.get()
                if threading.active_count() == 1:
                    src_thread = threading.Thread(target=build_metadata,
                                                  kwargs={'queue': src_metadata_queue,
                                                 'session': imap_session,
                                                 'folder': src_folder,
                                                 'search_criteria': '(FROM "{}")'.format(auth['email']['recv_reports_from_address'])})
                    src_thread.start()
                    dest_thread = threading.Thread(target=build_metadata,
                                                   kwargs={'queue': dest_metadata_queue,
                                                           'session': imap_session,
                                                           'folder': dest_folder,
                                                           'search_criteria': 'ALL'})
                    dest_thread.start()
                else:
                    print('thread in progress: skipping building metadata')  # FIXME
            else:
                src_messages_metadata = build_metadata(queue=src_metadata_queue,
                                                       session=imap_session,
                                                       folder=src_folder,
                                                       search_criteria='(FROM "{}")'.format(auth['email']['recv_reports_from_address']))
                dest_messages_metadata = build_metadata(queue=dest_metadata_queue,
                                                        session=imap_session,
                                                        folder=dest_folder,
                                                        search_criteria='ALL')

            # dest_message_ids = mail.get_message_ids(session=imap_session,
            #                                         folder=dest_folder)
            # dest_messages_metadata = mail.get_messages_metadata(imap_session, dest_message_ids) if dest_message_ids != [''] else {}
            if src_messages_metadata is None or dest_messages_metadata is None:
                print('metadata does not exist: sleep and continue loop')  # FIXME
                time.sleep(config['sleep_time_between_checks'])
                continue
            unique_subjects = get_unique_dict_keys(src_messages_metadata, dest_messages_metadata)
            if len(unique_subjects) > 0:
                print('processing {} unique messages not in destination folder')  # FIXME
            else:
                print('no unique messages found: sleep and continue loop')  # FIXME
                time.sleep(config['sleep_time_between_checks'])
                continue

            with tempfile.TemporaryDirectory() as downloads_dir:
                for subject in sorted(unique_subjects, key=lambda x: int(src_messages_metadata[x]['message_id'])):
                    print('processing id {}'.format(int(src_messages_metadata[subject]['message_id'])))  # TODO: remove - testing
                    attachment = mail.download_attachment(imap_session, src_folder, src_messages_metadata[subject]['message_id'], downloads_dir)
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
                print('message processing completed: sleep and continue loop')  # FIXME
                time.sleep(config['sleep_time_between_checks'])
