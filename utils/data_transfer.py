from os import makedirs

from air_pressure.mongodb_operations.mongo_operations import MongoDB_Operation
from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Data_Transfer:
    def __init__(self):
        self.mongo_op = MongoDB_Operation()

        self.config = read_params()

        self.s3 = S3_Operation()

        self.train_batch = self.config["data"]["raw_data"]["train_batch"]

        self.pred_batch = self.config["data"]["raw_data"]["pred_batch"]

        self.raw_data_bucket_name = self.config["s3_bucket"][
            "air_pressure_raw_data_bucket"
        ]

        self.log_file = self.config["log"]["data_transfer"]

        self.db_name = self.config["mongodb"]["air_pressure_data_db_name"]

        self.folder_name = self.config["raw_data_folder_name"]

        self.split_ratio = self.config["data_split_ratio"]

        self.log_writer = App_Logger()

    def transfer_mongo_raw_data_to_s3_bucket(self):
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.transfer_mongo_raw_data_to_s3_bucket.__name__,
            __file__,
            self.log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.log_writer.log(
                "Started transferring raw data from mongodb to s3 buckets", **log_dic
            )

            makedirs(self.folder_name, exist_ok=True)

            self.mongo_op.get_collections_as_csv_batch(
                self.folder_name, self.db_name, self.log_file
            )

            self.s3.upload_folder(
                self.folder_name,
                self.raw_data_bucket_name,
                self.log_file,
                remove_folder=True,
            )

            self.log_writer.log(
                "Transferred raw data from mongodb to s3 buckets", **log_dic
            )

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def list_splitter(self, list_to_split, ratio):
        try:
            elements = len(list_to_split)

            middle = int(elements * ratio)

            return list_to_split[:middle], list_to_split[middle:]

        except Exception as e:
            raise e

    def transfer_files(self, lst, folder, bucket):
        try:
            self.s3.create_folder(folder, bucket, self.log_file)

            for f in lst:
                dest_f = folder + "/" + f.split("/")[1]

                self.s3.copy_data(f, bucket, dest_f, bucket, self.log_file)

        except Exception as e:
            raise e

    def split_raw_data(self):
        try:
            files = self.s3.get_files_from_folder(
                self.folder_name, self.raw_data_bucket_name, self.log_file
            )

            train, pred = self.list_splitter(files, self.split_ratio)

            self.transfer_files(train, self.train_batch, self.raw_data_bucket_name)

            self.transfer_files(pred, self.pred_batch, self.raw_data_bucket_name)

        except Exception as e:
            raise e

    def transfer_and_split_data_from_mongodb(self):
        try:
            self.transfer_mongo_raw_data_to_s3_bucket()
            
            # if train and pred folder does not exist run the split_raw_data func, 
            # else run transfer_mongo_raw_data_to_pred_s3_bucket

            self.split_raw_data()

        except Exception as e:
            raise e
