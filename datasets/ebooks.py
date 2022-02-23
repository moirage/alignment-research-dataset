import ebooks
import argparse
import os
import pypandoc
from pypandoc.pandoc_download import download_pandoc

def cmd_list(args):
    for name in ebooks.ALL_EBOOKS:
        print(name)

def cmd_fetch(args):
    ebooks.get_ebook(args.name).fetch()

def create_arg_parser():
    parser = argparse.ArgumentParser(description='Fetch ebooks.')
    subparsers = parser.add_subparsers(title='commands',
                                       description='valid commands',
                                       help='additional help')

    list_cmd = subparsers.add_parser('list', help='List available ebooks.')
    list_cmd.set_defaults(func=cmd_list)

    fetch_cmd = subparsers.add_parser('fetch', help='Fetch ebooks.')
    fetch_cmd.set_defaults(func=cmd_fetch)
    fetch_cmd.add_argument('name', help='Name of ebook to fetch.')
    fetch_cmd.add_argument('--path', default='data/ebooks', help='Path to save ebooks.')
    parser.add_argument('--install-pandoc', action='store_true', help='Install pandoc.')
    return parser

def main():
    args = create_arg_parser().parse_args()
    if args.install_pandoc:
        os.makedirs(os.getcwd()+'/pandoc') if not os.path.exists(os.getcwd()+'/pandoc') else ''
        download_pandoc(targetfolder=os.getcwd()+'/pandoc/')

    if getattr(args, 'func', None) is None:
        # No subcommand was given
        create_arg_parser().print_help()
        return
    
    args.func(args)

if __name__ == '__main__':
    main()
