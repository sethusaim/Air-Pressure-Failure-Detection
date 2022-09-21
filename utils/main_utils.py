from os import makedirs

from air_pressure.mongodb_operations.mongo_operations import MongoDB_Operation
from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Main_Utils:
    """
    Description :   This class shall be used to find the model with best accuracy and AUC score.
    Version     :   1.2
    
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self, log_file):
        self.log_file = log_file

        self.config = read_params()

        self.model_bucket = self.config["s3_bucket"]["air_pressure_model_bucket"]

        self.good_train_data_dir = self.config["data"]["train"]["good_data_dir"]

        self.bad_train_data_dir = self.config["data"]["train"]["bad_data_dir"]

        self.train_data_bucket = self.config["s3_bucket"][
            "air_pressure_train_data_bucket"
        ]

        self.s3 = S3_Operation()

        self.log_writer = App_Logger()

    def create_model_folders(self, log_file):
        """
        Method Name :   create_model_folders
        Description :   This methods creates the model folder
        
        Output      :   Model folders are created in s3 buckets
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.create_model_folders.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            model_dir_lst = list(self.config["model_dir"].values())

            self.log_writer.log("Got a list of model folders", **log_dic)

            [
                self.s3.create_folder(folder, self.model_bucket, log_file)
                for folder in model_dir_lst
            ]

            self.log_writer.log("Created model folders in s3 bucket", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def create_dirs_for_good_bad_data(self, log_file):
        """
        Method Name :   create_dirs_for_good_bad_data
        Description :   This method creates folders for good and bad data in s3 bucket
        Output      :   Good and bad folders are created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            "main_utils.py",
            self.create_dirs_for_good_bad_data.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.s3.create_folder(
                self.good_train_data_dir, self.train_data_bucket, log_file
            )

            self.s3.create_folder(
                self.bad_train_data_dir, self.train_data_bucket, log_file
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

