from argparse import ArgumentParser

from dorker import DorkSearch, console


def main():
    parser = ArgumentParser(description="Scrape URLs using Dork")
    parser.add_argument("-d", "--dork", type=str, help="Dorks")
    parser.add_argument("-w", "--worker", type=int, help="How many worker")
    parser.add_argument("-a", "--amount", type=int, help="How many URLs to be scrape")
    parser.add_argument("-i", "--info", action="store_true", help="Status info")
    parser.add_argument("-f", "--file", type=str, help="Output filename (Without Ext)")
    args = parser.parse_args()

    dork_search = DorkSearch()
    dork_search.start_program(
        dork=args.dork,
        worker=args.worker,
        amount=args.amount,
        file_name=args.file,
        info=args.info,
    )


if __name__ == "__main__":
    console.clear()
    main()
