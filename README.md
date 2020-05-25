# email_parser

This application was developed as a project to showcase various language specific techniques to prospective employers, whilst also being a useful tool within the cyber security field.

This application takes with a single email file (currently only tested against .eml file extensions), or a directory of email files. Each file will be instantiated into an object, and examined for any embedded links or attachments.

If a Virustotal API key is provided, the extracted links and/or attachments will be synchronously queried for any known malicious links.

If the '--write_attachments' flag is specified, any identified attachments will be written to a results directory for further analysis. Additionally, if the email file contains a zipped attachment, it will unzip and extract the original file.

Note: this is still a work in progress.

## Usage

The email parser script accepts two variations of ingesting an email file. One is to pass through STDIN, so that other applications can pass the email file in memory. The second is passing in a path & filename as shown below.

Setup dependencies and run
```bash
$ pipenv shell
$ pipenv install
$ python3 -m emailparser -h
```

Menu Options
```bash
usage: __main__.py [-h] [--stdin] [--file FILE] [--out-file OUT_FILE]
                   [--write_attachments] [--vt_api VT_API]

optional arguments:
  -h, --help           show this help message and exit
  --stdin              listens on stdin for an email file
  --file FILE          supply path to email file
  --out-file OUT_FILE  name of directory to store the results
  --write_attachments  select flag to indicate you wish for any attachments to
                       be written to disk
  --vt_api VT_API      provide API key for virustotal if reputational stats
                       are required
```

## Techniques Used

* CLI Arguments
* JSON encoding
* OOP
* Decorators
* Collection Deque
* Asyncio
* Error Handling

## Roadmap

* Add unittests for the EmailFile class object
* Finish stdin/stdout functionality
  * To be able to accept stream from another application and return results
* Test link/attachment identification functions against a larger sample pool

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
