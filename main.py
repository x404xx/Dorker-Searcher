from argparse import ArgumentParser
from os import name, system

from dorker import DorkSearch


def main():
    parser = ArgumentParser(description='DorkSearch')
    parser.add_argument('-d', '--dork', type=str, help='Dorks')
    parser.add_argument('-w', '--worker', type=int, help='How many worker')
    parser.add_argument('-a', '--amount', type=int, help='How many URLs to be scrape')
    parser.add_argument('-i', '--info', action='store_true', help='Status info')
    parser.add_argument('-s', '--save', action='store_true', help='Save output')
    parser.add_argument('-f', '--file', type=str, help='Output file name')
    args = parser.parse_args()

    dork_search = DorkSearch()
    dork_search.run(
        dork=args.dork,
        worker=args.worker,
        amount=args.amount,
        info=args.info,
        save_output=args.save,
        file_name=args.file
    )


if __name__ == '__main__':
    system('cls' if name == 'nt' else 'clear')
    main()
