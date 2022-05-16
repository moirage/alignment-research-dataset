import argparse
import json
import os
from collections import OrderedDict
from urllib.parse import urlparse

import blogs
from blogs.utils import EntryWriter

def cmd_list(args):
    for name in blogs.ALL_BLOGS:
        print(name)

def cmd_fetch(args):
    with EntryWriter(args.name, args.path) as writer:
        for entry in blogs.get_blog(args.name).fetch_entries():
            writer.write(entry)

def create_arg_parser():
    parser = argparse.ArgumentParser(description='Fetch blog posts.')
    subparsers = parser.add_subparsers(title='commands',
                                       description='valid commands',
                                       help='additional help')

    list_cmd = subparsers.add_parser('list', help='List available blogs.')
    list_cmd.set_defaults(func=cmd_list)

    fetch_cmd = subparsers.add_parser('fetch', help='Fetch blog posts.')
    fetch_cmd.set_defaults(func=cmd_fetch)
    fetch_cmd.add_argument('name', help='Name of blog to fetch.')
    fetch_cmd.add_argument('--path', default='data/blogs', help='Path to save blog posts.')

    return parser

def main():
    args = create_arg_parser().parse_args()

    if getattr(args, 'func', None) is None:
        # No subcommand was given
        parser.print_help()
        return

    args.func(args)

if __name__ == '__main__':
    main()
