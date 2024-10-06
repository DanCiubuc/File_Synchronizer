import argparse
import pathlib
import os


class SameDirectoriesException(Exception):
    pass


def init_cli():
    parser = argparse.ArgumentParser(
        prog="sync_file",
        description="Synchronize two directories",
    )
    parser.add_argument("source-path", type=pathlib.Path)

    parser.add_argument("replica-path", type=pathlib.Path)

    parser.add_argument("sync-interval", nargs="?", type=int, default=60)

    parser.add_argument(
        "log-file-path", nargs="?", type=pathlib.Path, default="log.txt"
    )

    args = vars(parser.parse_args())

    if args["source-path"] == args["replica-path"]:
        raise SameDirectoriesException(
            "The source directory must be different from the replica directory."
        )

    if not os.path.exists(args["source-path"]) or not os.path.exists(
        args["replica-path"]
    ):
        raise NotADirectoryError(
            "The provided directory {directory} doesn't exist".format(
                directory=NotADirectoryError.filename
            )
        )

    return args
