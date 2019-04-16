import argparse
from zlm_sender import command


def main():
    parser = argparse.ArgumentParser(description="ZLayerManager bridge (communicate from zbrush to the UI)")

    parser.add_argument('--open', '-o', action='store_true', help='Open the UI if not already openened')
    parser.add_argument('--file', '-f', type=str, help='Layer file path')

    parser.add_argument('--import_file', '-i', type=str, help='Import file software')

    args = parser.parse_args()

    if args.open:
        command.open(args.file)

    elif args.import_file:
        command.maya_import(args.import_file)


if __name__ == "__main__":
    main()
