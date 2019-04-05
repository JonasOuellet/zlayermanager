import argparse
from zlm_sender import command


def main():
    parser = argparse.ArgumentParser(description="ZLayerManager bridge (communicate from zbrush to the UI)")

    parser.add_argument('--open', '-o', action='store_true', help='Open the UI if not already openened')
    parser.add_argument('--file', '-f', type=str, help='Layer file path')

    args = parser.parse_args()

    if args.open:
        command.open(args.file)


if __name__ == "__main__":
    main()
