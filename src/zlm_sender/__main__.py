import argparse
from zlm_sender import command


def main():
    parser = argparse.ArgumentParser(description="ZLayerManager bridge (communicate from zbrush to the UI)")

    parser.add_argument('--open', '-o', action='store_true', help='Open the UI if not already opened')
    parser.add_argument('--file', '-f', type=str, help='Layer file path')

    parser.add_argument('--import_file', '-i', type=str, help='Import file in application')

    parser.add_argument('--update-zbrush', '-uz', action='store_true', help='update zbrush with layer from zlm. if opened')
    parser.add_argument('--update', '-u', action='store_true', help='Update zlm ui with zbrush layer if opened')

    args = parser.parse_args()

    if args.open:
        command.open(args.file)

    elif args.import_file:
        command.app_import(args.import_file)

    elif args.update:
        command.update_from_zbrush()

    elif args.update_zbrush:
        command.update_zbrush()


if __name__ == "__main__":
    main()
