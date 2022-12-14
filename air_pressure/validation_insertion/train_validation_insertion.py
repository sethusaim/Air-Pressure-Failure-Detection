from air_pressure.data_transform.data_transformation_train import Data_Transform_Train
from air_pressure.data_type_valid.data_type_valid_train import DB_Operation_Train
from air_pressure.raw_data_validation.train_data_validation import (
    Raw_Train_Data_Validation,
)
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Train_Validation:
    """
    Description :   This class is used for validating all the training batch files
    Written by  :   iNeuron Intelligence
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.raw_data = Raw_Train_Data_Validation()

        self.data_transform = Data_Transform_Train()

        self.db_operation = DB_Operation_Train()

        self.config = read_params()

        self.train_main_log = self.config["log"]["train_main"]

        self.good_data_db_name = self.config["mongodb"]["air_pressure_data_db_name"]

        self.good_data_collection_name = self.config["mongodb"][
            "air_pressure_train_data_collection"
        ]

        self.log_writer = App_Logger()

    def training_validation(self):
        """
        Method Name :   training_validation
        Description :   This method is responsible for converting raw data to cleaned data for training

        Output      :   Raw data is converted to cleaned data for training
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.training_validation.__name__,
            __file__,
            self.train_main_log,
        )

        try:
            self.log_writer.start_log("start", **log_dic)

            (
                LengthOfDateStampInFile,
                LengthOfTimeStampInFile,
                _,
                noofcolumns,
            ) = self.raw_data.values_from_schema()

            regex = self.raw_data.get_regex_pattern()

            self.raw_data.validate_raw_fname(
                regex, LengthOfDateStampInFile, LengthOfTimeStampInFile
            )

            self.raw_data.validate_col_length(NumberofColumns=noofcolumns)

            self.raw_data.validate_missing_values_in_col()

            self.log_writer.log("Raw Data Validation Completed !!", **log_dic)

            self.log_writer.log("Starting Data Transformation", **log_dic)

            self.data_transform.add_quotes_to_string()

            self.log_writer.log("Data Transformation completed !!", **log_dic)

            self.db_operation.insert_good_data_as_record(
                self.good_data_db_name, self.good_data_collection_name
            )

            self.log_writer.log(
                "Data type validation Operation completed !!", **log_dic
            )

            self.db_operation.export_collection_to_csv(
                self.good_data_db_name, self.good_data_collection_name
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)
