import logging
import os
import time
import tomllib
import time
import shutil
import sys
import enum
import filecmp
import pathlib


class sync:
    """
    Class used to encapsulate the synchronization logic.

    Attributes
    ----------
    source_path: str
        Either the absolute path or the relative path, in relation to the script's directory, for the source folder.
    dest_path : str
        Either the absolute path or the relative path, in relation to the script's directory, for the destination (replica) folder.
    interval : int
        Synchronization interval.
    log_path : str
        Either the absolute path or the relative path, in relation to the script's directory, for the log file.

    Methods
    -------
    sync_files()
        Starts the synchronization process.
    """

    # ENUM class for sync operations. Used for logging.
    class SyncOperations(enum.Enum):
        CREATE = 1
        COPY = 2
        DELETE = 3

    def __init__(self, source_path: str, dest_path: str, interval: int, log_path: str):
        # convert to absolute paths - useful for logging.
        self.source_path = os.path.abspath(source_path)
        self.dest_path = os.path.abspath(dest_path)
        self.interval = interval

        # set up logger.
        logging.basicConfig(
            filename=log_path,
            filemode="a+",
            format="%(asctime)s, %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )

        self.log = logging.getLogger()
        # add handler so the log also outputs to stdout.
        self.log.addHandler(logging.StreamHandler(sys.stdout))

        # open TOML file.
        with open("pyproject.toml", "rb") as f:
            self.config = tomllib.load(f)

    def sync_files(self) -> None:
        while True:
            print("Synchronizing...")

            self.__sync_files(self.source_path, self.dest_path)

            # update timestamp
            self.timestamp = time.time()

            if self.config.get("debugMode"):
                time.sleep(60)
            else:
                time.sleep(self.interval)

    """
        Recursive method used to navigate, compare and synchronize the files inside the source and replica folders. 
        
        Parameters
        ----------
        src_folder: str
            Path for the source folder. 
        dest_folder: str
            Path for the dest folder.
    """

    def __sync_files(self, src_folder: str, dest_folder: str) -> None:
        compared = filecmp.dircmp(src_folder, dest_folder)

        try:
            # files/subdirectories only found in src_folder.
            if compared.left_only:
                for f in compared.left_only:
                    self.__create_file(
                        os.path.join(src_folder, f), os.path.join(dest_folder, f)
                    )

            # files/subdirectories only found in dest_folder.
            if compared.right_only:
                for f in compared.right_only:
                    self.__purge_from_dest(os.path.join(dest_folder, f))

            """ 
            Note: dircmp.diff_files stores all the files that are in both directories, 
            but whose os.stat() signatures are different including, among others, the modification time.
            Read more: https://docs.python.org/3/library/filecmp.html
            """
            # files/subdirectories that exist in both directories but have different timestamps.
            if compared.diff_files:
                for f in compared.diff_files:
                    self.__copy_file(
                        os.path.join(src_folder, f), os.path.join(dest_folder, f)
                    )

            # apply recursive functions to the subdirectories.
            for subdir in compared.common_dirs:
                self.__sync_files(
                    os.path.join(src_folder, subdir), os.path.join(dest_folder, subdir)
                )
        # important in the case a file gets removed during the synchronization process.
        except FileNotFoundError:
            file_to_remove = os.path.join(
                FileNotFoundError.__dir__(), FileNotFoundError.filename
            )
            self.__purge_from_dest(file_to_remove)

    """
        Helper method used to create a file inside the replica directory. 
            
        Parameters
        ----------
        src_file_path: str
            Path for the original source file
        dest_file_path: str
            Path where the replica will be stored
    """

    def __create_file(self, src_file_path: str, dest_file_path: str) -> None:
        is_dir = os.path.isdir(src_file_path)

        if is_dir:
            shutil.copytree(src_file_path, dest_file_path, dirs_exist_ok=True)
        else:
            shutil.copy(src_file_path, dest_file_path)
        self.__write_to_log(dest_file_path, self.SyncOperations.CREATE, is_dir)

    """
        Helper method used to copy a file from the source directory to the replica directory. 
            
        Parameters
        ----------
        src_file_path: str
            Path for the original source file
        dest_file_path: str
            Path where the replica will be stored
    """

    def __copy_file(self, src_file_path: str, dest_file_path: str) -> None:
        is_dir = os.path.isdir(src_file_path)

        if is_dir:
            shutil.copytree(src_file_path, dest_file_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_file_path, dest_file_path)
        self.__write_to_log(dest_file_path, self.SyncOperations.COPY, is_dir)

    """
        Helper method for deleting from the replica directory.
        
        Parameters
        ----------
        
        source: dest_file_path
            Path of the file inside the replica directory that is going to be deleted.
    """

    def __purge_from_dest(self, dest_file_path: str) -> None:
        is_dir = os.path.isdir(dest_file_path)
        if is_dir:
            shutil.rmtree(dest_file_path)
        else:
            os.remove(dest_file_path)
        self.__write_to_log(dest_file_path, self.SyncOperations.DELETE, is_dir)

    """
        Helper method for logging, depending on the type of operation.
        
        Parameters
        ----------
        
        file_path: pathlib.Path
            Path of the file that was the target of the operation.
        operation: SyncOperations
            The type of operation to log.
        is_dir: bool
            Boolean that indicates if the file to log is a dir or not.
    """

    def __write_to_log(
        self, file_path: pathlib.Path, operation: SyncOperations, is_dir: bool = False
    ) -> None:
        if not isinstance(file_path, pathlib.Path):
            file_path = pathlib.Path(file_path)

        match operation:
            case self.SyncOperations.CREATE:
                self.log.info(
                    "{file_type} {file_name} created in {dest}".format(
                        file_type="Directory" if is_dir else "File",
                        file_name=file_path.name,
                        dest=os.path.abspath(file_path.parent),
                    )
                )

            case self.SyncOperations.COPY:
                self.log.info(
                    "{file_type} {file_name} content's copied to {dest}".format(
                        file_type="Directory" if is_dir else "File",
                        file_name=file_path.name,
                        dest=os.path.abspath(file_path.parent),
                    )
                )

            case self.SyncOperations.DELETE:
                self.log.info(
                    "{file_type} {file_name} deleted from {dest}".format(
                        file_type="Directory" if is_dir else "File",
                        file_name=file_path.name,
                        dest=os.path.abspath(file_path.parent),
                    )
                )
