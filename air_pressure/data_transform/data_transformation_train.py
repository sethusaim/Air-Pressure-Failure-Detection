from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Data_Transform_Train:
    """
    Description :  This class shall be used for transforming the training batch data before loading it in Database!!.
    
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.config = read_params()

        self.train_data_bucket = self.config["s3_bucket"][
            "air_pressure_train_data_bucket"
        ]

        self.s3 = S3_Operation()

        self.log_writer = App_Logger()

        self.good_train_data_dir = self.config["data"]["train"]["good_data_dir"]

        self.train_data_transform_log = self.config["log"]["train_data_transform"]

    def add_quotes_to_string(self):
        """
        Method Name :   add_quotes_to_string
        Description :   This method addes the quotes to the string data present in columns
        
        Output      :   A csv file where all the string values have quotes inserted
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.add_quotes_to_string.__name__,
            __file__,
            self.train_data_transform_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            lst = self.s3.read_csv_from_folder(
                self.good_train_data_dir,
                self.train_data_bucket,
                self.train_data_transform_log,
            )

            for _, t_pdf in enumerate(lst):
                df = t_pdf[0]

                file = t_pdf[1]

                abs_f = t_pdf[2]

                df["class"] = df["class"].apply(lambda x: "'" + str(x) + "'")

                for column in df.columns:
                    count = df[column][df[column] == "na"].count()

                    if count != 0:
                        df[column] = df[column].replace("na", "'na'")

                self.log_writer.log(f"Quotes added for the file {file}", **log_dic)

                self.s3.upload_df_as_csv(
                    df,
                    abs_f,
                    file,
                    self.train_data_bucket,
                    self.train_data_transform_log,
                )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)
