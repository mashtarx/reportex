import os
import json
import argparse
import pathlib
from reportex.core import FontsManager, BASE_DIR



def run():
    main_parser = argparse.ArgumentParser()

    subparsers = main_parser.add_subparsers(title="reportex commands", required=True)

    create_font_parser(subparsers)
    create_cache_parser(subparsers)
    

    args = main_parser.parse_args()
    args.fn(args)


def create_font_parser(main_subsparsers: argparse.ArgumentParser):
    font_parser = main_subsparsers.add_parser("font", help="")
    font_subparsers = font_parser.add_subparsers(title="font commands", required=True)
    fontlist_parser = font_subparsers.add_parser(
        "list", help="list all the available fonts"
    )
    fontlist_parser.set_defaults(fn=list_fonts)

    fontreg_parser = font_subparsers.add_parser(
        "register", help="this command is used to register ttf fonts"
    )
    fontreg_parser.add_argument("-ttf", "--ttf_file", help="path to ttf file")
    fontreg_parser.add_argument(
        "-n", "--name", help="the name to register the font against"
    )
    fontreg_parser.set_defaults(fn=handle_register_font)



def create_cache_parser(main_subparser: argparse._SubParsersAction):
    cache_parser = main_subparser.add_parser("cache")
    cache_subparsers = cache_parser.add_subparsers(title="cache commands", required=True)

    image_parser = cache_subparsers.add_parser("image")
    image_parser.add_argument("-cl", "--clear", action="store_true", help="clear the image cache")
    image_parser.set_defaults(fn=handle_image_parser)




def handle_image_parser(args):
    if not args.clear:
        return

    dr = BASE_DIR/"reportex"/"cache"
    for fl in os.listdir(dr):
        os.remove(dr/fl)
    with open(dr/"network_images.json", "w") as f:
        json.dump({}, f)



def list_fonts(args):
    print()
    print("fonts: ")
    for fnt in FontsManager.all_fonts:
        print("   ", fnt)
    print()


def handle_register_font(args):
    if not (args.ttf_file or args.name):
        print("[name] and [ttf] are required")
        return
    FontsManager.register_ttf(args.name, pathlib.Path(args.ttf_file))
    print(f"\nfont: [{args.name}] added successfully\n")
