from air_pressure.mongodb_operations.mongo_operations import MongoDB_Operation
from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class DB_Operation_Pred:
    """
    Description :    This class shall be used for handling all the db operations
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.config = read_params()

        self.pred_data_bucket = self.config["s3_bucket"][
            "air_pressure_pred_data_bucket"
        ]

        self.pred_export_csv_file = self.config["export_csv_file"]["pred"]

        self.good_data_pred_dir = self.config["data"]["pred"]["good_data_dir"]

        self.input_files_bucket = self.config["s3_bucket"]["input_files_bucket"]

        self.pred_db_insert_log = self.config["log"]["pred_db_insert"]

        self.pred_export_csv_log = self.config["log"]["pred_export_csv"]

        self.s3 = S3_Operation()

        self.mongo = MongoDB_Operation()

        self.log_writer = App_Logger()

    def insert_good_data_as_record(self, good_data_db_name, good_data_collection_name):
        """
        Method Name :   insert_good_data_as_record
        Description :   This method inserts the good data in MongoDB as collection

        Output      :   A MongoDB collection is created with good data present in it
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.insert_good_data_as_record.__name__,
            __file__,
            self.pred_db_insert_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            lst = self.s3.read_csv_from_folder(
                self.good_data_pred_dir, self.pred_data_bucket, self.pred_db_insert_log,
            )

            for _, f in enumerate(lst):
                df = f[0]

                file = f[1]

                if file.endswith(".csv"):
                    self.mongo.insert_dataframe_as_record(
                        df,
                        db_name=good_data_db_name,
                        collection_name=good_data_collection_name,
                        log_file=self.pred_db_insert_log,
                    )

                else:
                    pass

                self.log_writer.log(
                    "Inserted dataframe as collection record in mongodb", **log_dic
                )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def export_collection_to_csv(self, good_data_db_name, good_data_collection_name):
        """
        Method Name :   insert_good_data_as_record
        Description :   This method inserts the good data in MongoDB as collection

        Output      :   A csv file stored in input files bucket, containing good data which was stored in MongoDB
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.export_collection_to_csv.__name__,
            __file__,
            self.pred_export_csv_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            df = self.mongo.get_collection_as_dataframe(
                db_name=good_data_db_name,
                collection_name=good_data_collection_name,
                log_file=self.pred_export_csv_log,
            )

            self.s3.upload_df_as_csv(
                df,
                self.pred_export_csv_file,
                self.pred_export_csv_file,
                self.input_files_bucket,
                self.input_files_bucket,
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)
