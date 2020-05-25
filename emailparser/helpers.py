import argparse


# CLI Argument Decorator
def cli_args(func):
    # decorator function for CLI menu
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stdin", help="listens on stdin for an email file", action="store_true")
    parser.add_argument("--file", help="supply path to email file")
    parser.add_argument("--out-file", help="name of directory to store the results")
    parser.add_argument("--write_attachments", help="select flag to indicate you wish for any attachments to be written to disk", action="store_true")
    parser.add_argument("--vt_api", help="provide API key for virustotal if reputational stats are required")

    def arg_func():
        args = parser.parse_args()
        return func(args)
    return arg_func
