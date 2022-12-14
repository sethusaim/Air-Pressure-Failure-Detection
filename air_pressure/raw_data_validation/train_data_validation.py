import re

from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.main_utils import Main_Utils
from utils.read_params import get_log_dic, read_params


class Raw_Train_Data_Validation:
    """
    Description :   This method is used for validating the raw training data
    Written by  :   iNeuron Intelligence
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.config = read_params()

        self.raw_data_bucket = self.config["s3_bucket"]["air_pressure_raw_data_bucket"]
        self.log_writer = App_Logger()

        self.s3 = S3_Operation()

        self.utils = Main_Utils()

        self.input_files_bucket = self.config["s3_bucket"]["input_files_bucket"]

        self.train_data_bucket = self.config["s3_bucket"][
            "air_pressure_train_data_bucket"
        ]

        self.raw_train_data_dir = self.config["data"]["raw_data"]["train_batch"]

        self.good_train_data_dir = self.config["data"]["train"]["good_data_dir"]

        self.bad_train_data_dir = self.config["data"]["train"]["bad_data_dir"]

        self.train_schema_file = self.config["schema_file"]["train_schema_file"]

        self.regex_file = self.config["regex_file"]

        self.train_schema_log = self.config["log"]["train_values_from_schema"]

        self.train_gen_log = self.config["log"]["train_general"]

        self.train_name_valid_log = self.config["log"]["train_name_validation"]

        self.train_col_valid_log = self.config["log"]["train_col_validation"]

        self.train_missing_value_log = self.config["log"]["train_missing_values_in_col"]

    def values_from_schema(self):
        """
        Method Name :   values_from_schema
        Description :   This method gets schema values from the schema_training.json file

        Output      :   Schema values are extracted from the schema_training.json file
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.values_from_schema.__name__,
            __file__,
            self.train_schema_log,
        )

        try:
            self.log_writer.start_log("start", **log_dic)

            dic = self.s3.read_json(
                self.train_schema_file, self.input_files_bucket, self.train_schema_log,
            )

            LengthOfDateStampInFile = dic["LengthOfDateStampInFile"]

            LengthOfTimeStampInFile = dic["LengthOfTimeStampInFile"]

            column_names = dic["ColName"]

            NumberofColumns = dic["NumberofColumns"]

            message = (
                "LengthOfDateStampInFile:: %s" % LengthOfDateStampInFile
                + "\t"
                + "LengthOfTimeStampInFile:: %s" % LengthOfTimeStampInFile
                + "\t "
                + "NumberofColumns:: %s" % NumberofColumns
                + "\n"
            )

            self.log_writer.log(message, **log_dic)

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

        return (
            LengthOfDateStampInFile,
            LengthOfTimeStampInFile,
            column_names,
            NumberofColumns,
        )

    def get_regex_pattern(self):
        """
        Method Name :   get_regex_pattern
        Description :   This method gets regex pattern from input files s3 bucket

        Output      :   A regex pattern is extracted
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_regex_pattern.__name__,
            __file__,
            self.train_gen_log,
        )

        try:
            self.log_writer.start_log("start", **log_dic)

            regex = self.s3.read_text(
                self.regex_file, self.input_files_bucket, self.train_gen_log,
            )

            self.log_writer.log(f"Got {regex} pattern", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return regex

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def validate_raw_fname(
        self, regex, LengthOfDateStampInFile, LengthOfTimeStampInFile
    ):
        """
        Method Name :   validate_raw_fname
        Description :   This method validates the raw file name based on regex pattern and schema values

        Output      :   Raw file names are validated, good file names are stored in good data folder and rest is stored in bad data
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.validate_raw_fname.__name__,
            __file__,
            self.train_name_valid_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.utils.create_dirs_for_good_bad_data(self.train_name_valid_log)

            onlyfiles = self.s3.get_files_from_folder(
                self.raw_train_data_dir, self.raw_data_bucket, self.train_name_valid_log
            )

            train_batch_files = [f.split("/")[1] for f in onlyfiles]

            self.log_writer.log("Got training files with absolute file name", **log_dic)

            for fname in train_batch_files:
                raw_data_train_fname = self.raw_train_data_dir + "/" + fname

                good_data_train_fname = self.good_train_data_dir + "/" + fname

                bad_data_train_fname = self.bad_train_data_dir + "/" + fname

                self.log_writer.log("Created raw,good and bad data file name", *log_dic)

                if re.match(regex, fname):
                    splitAtDot = re.split(".csv", fname)

                    splitAtDot = re.split("_", splitAtDot[0])

                    if len(splitAtDot[1]) == LengthOfDateStampInFile:
                        if len(splitAtDot[2]) == LengthOfTimeStampInFile:
                            self.s3.copy_data(
                                raw_data_train_fname,
                                self.raw_data_bucket,
                                good_data_train_fname,
                                self.train_data_bucket,
                                self.train_name_valid_log,
                            )

                        else:
                            self.s3.copy_data(
                                raw_data_train_fname,
                                self.raw_data_bucket,
                                bad_data_train_fname,
                                self.train_data_bucket,
                                self.train_name_valid_log,
                            )

                    else:
                        self.s3.copy_data(
                            raw_data_train_fname,
                            self.raw_data_bucket,
                            bad_data_train_fname,
                            self.train_data_bucket,
                            self.train_name_valid_log,
                        )
                else:
                    self.s3.copy_data(
                        raw_data_train_fname,
                        self.raw_data_bucket,
                        bad_data_train_fname,
                        self.train_data_bucket,
                        self.train_name_valid_log,
                    )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def validate_col_length(self, NumberofColumns):
        """
        Method Name :   validate_col_length
        Description :   This method validates the column length based on number of columns as mentioned in schema values

        Output      :   The files' columns length are validated and good data is stored in good data folder and rest is stored in bad data folder
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.validate_col_length.__name__,
            __file__,
            self.train_col_valid_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            lst = self.s3.read_csv_from_folder(
                self.good_train_data_dir,
                self.train_data_bucket,
                self.train_col_valid_log,
            )

            for _, f in enumerate(lst):
                df = f[0]

                file = f[1]

                abs_f = f[2]

                if file.endswith(".csv"):
                    if df.shape[1] == NumberofColumns:
                        pass

                    else:
                        dest_f = self.bad_train_data_dir + "/" + abs_f

                        self.s3.move_data(
                            file,
                            self.train_data_bucket,
                            dest_f,
                            self.train_data_bucket,
                            self.train_col_valid_log,
                        )

                else:
                    pass

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def validate_missing_values_in_col(self):
        """
        Method Name :   validate_missing_values_in_col
        Description :   This method validates the missing values in columns

        Output      :   Missing columns are validated, and good data is stored in good data folder and rest is to stored in bad data folder
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.validate_missing_values_in_col.__name__,
            __file__,
            self.train_missing_value_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            lst = self.s3.read_csv_from_folder(
                self.good_train_data_dir,
                self.train_data_bucket,
                self.train_missing_value_log,
            )

            for _, f in enumerate(lst):
                df = f[0]

                file = f[1]

                abs_f = f[2]

                if abs_f.endswith(".csv"):
                    count = 0

                    for cols in df:
                        if (len(df[cols]) - df[cols].count()) == len(df[cols]):
                            count += 1

                            dest_f = self.bad_train_data_dir + "/" + abs_f

                            self.s3.move_data(
                                file,
                                self.train_data_bucket,
                                dest_f,
                                self.train_data_bucket,
                                self.train_missing_value_log,
                            )

                            break

                    if count == 0:
                        dest_f = self.good_train_data_dir + "/" + abs_f

                        self.s3.upload_df_as_csv(
                            df,
                            abs_f,
                            dest_f,
                            self.train_data_bucket,
                            self.train_missing_value_log,
                        )

                else:
                    pass

                self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)
