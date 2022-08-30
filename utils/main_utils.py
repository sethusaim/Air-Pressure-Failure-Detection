import os

from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Main_Utils:
    def __init__(self):
        self.s3 = S3_Operation()

        self.log_writer = App_Logger()

        self.config = read_params()

        self.good_train_data_dir = self.config["data"]["train"]["good_data_dir"]

        self.bad_train_data_dir = self.config["data"]["train"]["bad_data_dir"]

        self.train_data_bucket = self.config["s3_bucket"][
            "air_pressure_train_data_bucket"
        ]

    def upload_logs(self, log_path, bucket):
        try:
            log_dir = os.listdir(log_path)

            for log in log_dir:
                abs_f = log_path + "/" + log

                self.s3.upload_file(abs_f, abs_f, bucket, "train_upload_log.txt")

            os.removedirs(log_path)

        except Exception as e:
            raise e

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
