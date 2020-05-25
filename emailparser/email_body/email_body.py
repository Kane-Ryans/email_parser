import io
import hashlib
import mimetypes
import zipfile
import re


class EmailFile:
    def __init__(self, msg, eml_filename: str = 'Stdin'):
        self.eml_filename = eml_filename
        self.msg = msg
        self.artifacts = []
        self.check_for_attachments()
        self.get_email_body()

    def create_attachment_instance(self, filename, file_bytes, file_extension=None):
        return self.Attachment(filename=filename, file_bytes=file_bytes, file_extension=file_extension)

    def check_for_attachments(self):
        print(f' - checking for attachments - ')
        for part in self.msg.walk():
            content_type = part.get_content_type()
            filename = part.get_filename()
            payload = part.get_payload(decode=True)
            # TODO: needs more testing against larger pool of samples
            # if 'image/' in content_type:
            #     continue
            if content_type == 'application/x-zip-compressed' or content_type == 'application/zip':
                self.unzip_attachment(payload)
            if filename is not None and len(payload) != 0:
                print(f'     ATTACHMENT FOUND: {filename}')
                attachment = self.Attachment(filename=filename, file_bytes=payload, file_extension=content_type)
                self.artifacts.append(attachment)

    def get_email_body(self):
        if self.msg.is_multipart():
            print(f' - checking for links - ')
            for part in self.msg.walk():
                content_type = part.get_content_type()
                content_disposition = ""
                if part.get('Content-Disposition') is not None:
                    content_disposition = part.get('Content-Disposition')
                if 'attachment' not in content_disposition:
                    if content_type == 'text/plain' or content_type == 'text/html':
                        self.check_for_links(part.get_payload())

        else:
            self.check_for_links(self.msg.get_payload())

    def check_for_links(self, email_body):
        try:
            href_pattern = re.compile(r"((?<=href=\")|(?<=href=3D\")).+?(?=\")", re.DOTALL)
            matches = re.finditer(href_pattern, email_body)
            for match in matches:
                cleaned_link = self.clean_link(match.group())
                link = self.Link(url=cleaned_link)
                print(f'     LINK FOUND: {link.url}')
                self.artifacts.append(link)
        except TypeError as e:
            print(f"ERROR: check_for_links from msg: {self.eml_filename}")
            print(f"ERROR: check_for_links type error: {e}")

    @staticmethod
    def clean_link(link: str) -> str:
        return link.strip().replace('=\r\n', '')

    def unzip_attachment(self, file):
        with zipfile.ZipFile(io.BytesIO(file)) as myzip:
            for zipinfo in myzip.infolist():
                with myzip.open(zipinfo) as myfile:
                    attach_instance = self.create_attachment_instance(
                        filename=zipinfo.filename,
                        file_bytes=myfile.read()
                    )
                    self.artifacts.append(attach_instance)

    class Attachment:
        def __init__(self, filename, file_bytes, file_extension=None):
            self.filename = filename
            self.bytes = file_bytes
            if file_extension:
                self.file_extension = self.get_file_extension(file_extension)
            self.hash = self.get_sha256_hash()
            self.vt_stats = {}

        @staticmethod
        def get_file_extension(file_extension):
            return mimetypes.guess_extension(file_extension)

        def get_sha256_hash(self):
            file_hash = hashlib.sha256()
            file_hash.update(self.bytes)
            return file_hash.hexdigest()

        def write_attachment(self):
            my_io = io.BytesIO()
            my_io.write(self.bytes)
            with open(self.filename, 'wb') as f:
                f.write(my_io.getbuffer())

    class Link:
        def __init__(self, url):
            self.url = url
            self.vt_stats = {}
