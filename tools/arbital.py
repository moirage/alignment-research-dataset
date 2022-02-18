import argparse
import os
import shutil
from tqdm import tqdm

from arbital.download import (
    ARBITAL_SUBSPACES,
    get_page,
    get_arbital_page_aliases,
)

DEFAULT_CACHE_DIR = 'data/cache/arbital'
DEFAULT_DATA_DIR = 'data/arbital'


def write_page(page, path):
    alias = page['alias']
    title = page['title']
    created = page['pageCreatedAt']
    text = page['text']
    # TODO: play with formatting here
    data = f"{title}\n\n{created}\n\n{text}"
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    fn = os.path.join(path, f'arbital_{alias}.txt')
    with open(fn, 'w') as f:
        f.write(data)

def cmd_list(args):
    aliases = get_arbital_page_aliases(
        subspace=args.subspace,
        cache_dir=args.cache_dir,
    )
    print(f'{len(aliases)} total pages in subspace `{args.subspace}`.')
    print(aliases)

def cmd_fetch(args):
    aliases = get_arbital_page_aliases(
        subspace=args.subspace,
        cache_dir=args.cache_dir,
    )
    assert args.alias in aliases, 'Article does not exist for this alias'
    page = get_page(
        args.alias,
        subspace=args.subspace,
        cache_dir=args.cache_dir
    )
    write_page(page=page, path=args.path)

def cmd_fetch_all(args):
    assert args.subspace in ARBITAL_SUBSPACES, 'Not a valid Arbital subspace.'
    aliases = get_arbital_page_aliases(
        subspace=args.subspace,
        cache_dir=args.cache_dir
    )
    for alias in tqdm(aliases, disable=not args.progress):
        page = get_page(alias, args.subspace, args.cache_dir)
        write_page(page=page, path=args.path)

def cmd_clear_cache(args):
    if os.path.exists(cache_dir):
        shutil.rmtree(args.cache_dir)

def create_arg_parser():
    parser = argparse.ArgumentParser(description='Fetch Arbital articles.')
    subparsers = parser.add_subparsers(title='commands',
                                       description='valid commands',
                                       help='additional help')

    list_cmd = subparsers.add_parser('list', help='List available Arbital article aliases.')
    list_cmd.add_argument('--subspace', default='ai_alignment', choices=ARBITAL_SUBSPACES, help='Arbital subspace')
    list_cmd.set_defaults(func=cmd_list)
    list_cmd.add_argument('--cache-dir', default=DEFAULT_CACHE_DIR, help='Path to save cached scrapes.')

    fetch_cmd = subparsers.add_parser('fetch', help='Fetch Arbital articles.')
    fetch_cmd.set_defaults(func=cmd_fetch)
    fetch_cmd.add_argument('alias', help='Alias of Arbital article to fetch.')
    fetch_cmd.add_argument('--subspace', default='ai_alignment', choices=ARBITAL_SUBSPACES, help='Arbital subspace')
    fetch_cmd.add_argument('--path', default=DEFAULT_DATA_DIR, help='Path to save article.')
    fetch_cmd.add_argument('--cache-dir', default=DEFAULT_CACHE_DIR, help='Path to save cached scrapes.')

    fetch_all_cmd = subparsers.add_parser('fetch-all', help='Fetch all Arbital articles.')
    fetch_all_cmd.set_defaults(func=cmd_fetch_all)
    fetch_all_cmd.add_argument('--subspace', default='ai_alignment', choices=ARBITAL_SUBSPACES, help='Arbital subspace')
    fetch_all_cmd.add_argument('--path', default=DEFAULT_DATA_DIR, help='Path to save articles.')
    fetch_all_cmd.add_argument('--cache-dir', default=DEFAULT_CACHE_DIR, help='Path to save cached scrapes.')
    fetch_all_cmd.add_argument('--progress', default=True, help='Show progress.')

    clear_cache_cmd = subparsers.add_parser('clear-cache', help='Clear the cache.')
    clear_cache_cmd.set_defaults(func=cmd_clear_cache)
    clear_cache_cmd.add_argument('--cache-dir', default=DEFAULT_CACHE_DIR, help='Path to save cached scrapes.')
    return parser

def main():
    args = create_arg_parser().parse_args()

    if getattr(args, 'func', None) is None:
        # No subcommand was given
        create_arg_parser().print_help()
        return

    args.func(args)

if __name__ == '__main__':
    main()

