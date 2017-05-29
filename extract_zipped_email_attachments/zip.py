import zipfile
import os
import re


class ZippedFile(object):
    def __init__(self, zip_file, password=None):
        self.zip_file = zip_file
        self.password = password
        self.zip_invalid = False

        if self.zip_file is None:
            print('expected zipfile, got None')  # FIXME
            self.zip_invalid = True
            return
        if not os.path.isfile(self.zip_file):
            print('{} does not exist'.format(self.zip_file))  # FIXME
            self.zip_invalid = True
            return
        if not zipfile.is_zipfile(self.zip_file):
            print('{} is not a zip file'.format(self.zip_file))
            self.zip_invalid = True
            return
        if not isinstance(self.password, str) or self.password == None:
            try:
                self.password = str(self.password)
            except:
                raise TypeError('password must be a string')

    def get_pdfs(self):
        """
        Return all PDF files included in the archive.
        :return: list
        """
        print('getting pdfs from zip archive')  # FIXME
        with zipfile.ZipFile(self.zip_file, 'r') as zipped_file:
            return [pdf for pdf in zipped_file.namelist() if re.match('.*\.pdf', pdf.lower())]

    def extract_file(self, member_name, extract_path):
        """
        Extract a single file from an archive.
        :param member_name: name of file in the zipped archive to extract
        :param extract_path: path to extract file to
        :return: None
        """
        # fully_qualified_filename = os.path.realpath(member_name)
        with zipfile.ZipFile(self.zip_file) as zipped_file:
            zipped_file.extract(member_name, path=extract_path, pwd=self.password.encode())
