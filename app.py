import email.message
import email.header
import re
import mimetypes
import zipfile
import hashlib
import io
import argparse
import sys

# -------------- TO DO --------------
# 1. if images have executable URLS e.g. .php extensions


# -------------- check + extract links --------------


def check_links(msg):
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            # set content-disposition to "" if .get method returns None
            # the None appears to error the conditional logic below
            cdispo = part.get(
                'Content-Disposition') if part.get('Content-Disposition') is not None else ""
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)
                break
            elif ctype == 'text/html' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = msg.get_payload(decode=True)

    href_expression = b"(?<=href=).+?(?=\")"
    links = re.findall(href_expression, body)

    if links:
        # turn byte string regex results into a normalized string
        return [link.decode('utf-8').replace("\"", "") for link in links]
    else:
        return []

# -------------- check + extract attachments --------------


def unzip(file):
    archive = []
    with zipfile.ZipFile(io.BytesIO(file)) as myzip:
        for zipinfo in myzip.infolist():
            with myzip.open(zipinfo) as myfile:
                archive.append({
                    "filename": zipinfo.filename,
                    "size": zipinfo.file_size,
                    "bytes": myfile.read(),
                    "hash": getHash(myfile.read(), 'sha256')
                })
    return archive


def getHash(bytes, alg):
    if alg == 'md5':
        h = hashlib.md5()
        h.update(bytes)
        return h.hexdigest()
    elif alg == 'sha1':
        h = hashlib.sha1()
        h.update(bytes)
        return h.hexdigest()
    elif alg == 'sha256':
        h = hashlib.sha256()
        h.update(bytes)
        return h.hexdigest()


def check_attachments(msg):
    attachments = []

    for part in msg.walk():
        if part.get_content_type() == 'application/x-zip-compressed':
            embedded_files = unzip(part.get_payload(decode=True))
            return embedded_files
        if part.get_filename():
            attachment = {}
            attachment["bytes"] = part.get_payload(decode=True)
            attachment["filename"] = part.get_filename()
            attachment["extension"] = mimetypes.guess_extension(
                part.get_content_type())
            attachment["hash"] = getHash(
                part.get_payload(decode=True), 'sha256')
            attachments.append(attachment)

    return attachments


# -------------- file based actions --------------

def read_file(path):
    try:
        email_raw = open(path, 'rb')
        email_file = email_raw.read()
        email_raw.close()
        msg_in = email.message_from_bytes(email_file)
        assert isinstance(msg_in, email.message.Message)
        return msg_in
    except OSError as err:
        print(err)


def write_attachment_file(files):
    for file in files:
        myio = io.BytesIO()
        myio.write(file["bytes"])
        with open(file["filename"], "wb") as outfile:
            outfile.write(myio.getbuffer())


def write_links_file(links):
    with open('extracted_links.txt', "w") as outfile:
        for link in links:
            outfile.write(str(link))

# -------------- stdin based actions --------------


def read_stdin():
    stdin_binary = sys.stdin.detach()
    eml_in = stdin_binary.read()
    msg_in = email.message_from_bytes(eml_in)
    assert isinstance(msg_in, email.message.Message)
    return msg_in


# -------------- script entry point --------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stdin", help="listens on stdin for an email file", action="store_true")
    parser.add_argument("--file", help="supply path to email file")
    args = parser.parse_args()
    # --------------------------
    if args.stdin:
        msg_in = read_stdin()
        links = check_links(msg_in)
        if links:
            for link in links:
                print(link)
        attachments = check_attachments(msg_in)
        if attachments:
            for attachment in attachments:
                print(attachment)
    elif args.file:
        msg_in = read_file(args.file)
        links = check_links(msg_in)
        attachments = check_attachments(msg_in)
        if attachments:
            write_attachment_file(attachments)
        if links:
            write_links_file(links)


if __name__ == "__main__":
    main()
