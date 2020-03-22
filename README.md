# email_parser

This script was developed to accept an email file as input, to automatically extract links and attachments for further processing with other tools/APIs.

Links will be output to a file called 'extracted_links.txt' in the same directory as the script.
Attachments will be extracted to the same directory as the script.
Zipped attachments will be automatically unzipped and extracted.

Note: this is still a work in progress.

## Usage

The email parser script accepts two variations of ingesting an email file. One is to pass through STDIN, so that other applications can pass the email file in memory. The second is passing in a path & filename as shown below.

```bash
$ python3 app.py --stdin
```
or
```bash
$ python3 app.py --file ./email_samples/my_email.eml
```

optional arguments:
  -h, --help   show this help message and exit
  --stdin      listens on stdin for an email file
  --file FILE  supply path to email file
  
## Roadmap

* Needs testing against a larger sample pool of email files and email file types.
* All the various ways a link can be supplied in an email need to be explored and added to the script.
* Add detections for suspicious occurrences, such as:
    - an image tag pointing to an executable URL e.g. .php
    - differences in the from & reply-to fields (possible spoofing) - needs research/testing
    - and many more :)

## Contributing

The email_parser was created as a project for my portfolio of work. Anybody who wishes to fork the repo and continue adding features/further development are more than welcome.

## License

MIT License

Copyright (c) 2020 Kane Ryans

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
