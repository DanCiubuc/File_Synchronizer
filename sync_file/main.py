import cli
import sync

"""
    Author: Dan Ciubuc
    Email: dan.ciubuc1223@gmail.com
"""

if __name__ == "__main__":
    # get arguments from the user.
    args = cli.init_cli()

    # initialize sync object.
    sync_program = sync.sync(
        args["source-path"],
        args["replica-path"],
        args["sync-interval"],
        args["log-file-path"],
    )

    # start synchronization process.
    sync_program.sync_files()
