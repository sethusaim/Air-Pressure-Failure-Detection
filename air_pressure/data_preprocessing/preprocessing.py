import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.decomposition import PCA
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Preprocessor:
    """
    Description :   This class shall  be used to clean and transform the data before training.
    Version     :   1.2
    Revisions   :   moved setup to cloud
    """

    def __init__(self, log_file):
        self.log_writer = App_Logger()

        self.config = read_params()

        self.log_file = log_file

        self.knn_neighbours = self.config["knn_imputer"]["n_neighbors"]

        self.knn_weights = self.config["knn_imputer"]["weights"]

        self.null_values_file = self.config["null_values_csv_file"]

        self.n_components = self.config["pca_model"]["n_components"]

        self.input_files_bucket = self.config["s3_bucket"]["input_files_bucket"]

        self.s3 = S3_Operation()

    def remove_columns(self, data, columns):
        """
        Method Name :   remove_columns
        Description :   This method removes the given columns from a pandas dataframe.
        
        Output      :   A pandas DataFrame after removing the specified columns.
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.remove_columns.__name__,
            __file__,
            self.log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        self.data = data

        self.columns = columns

        try:
            self.useful_data = self.data.drop(labels=self.columns, axis=1)

            self.log_writer.log(f"Dropped {columns} from {data}", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return self.useful_data

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def separate_label_feature(self, data, label_column_name):
        """
        Method Name :   separate_label_feature
        Description :   This method separates the features and a Label Coulmns.
        
        Output      :   Returns two separate dataframes, one containing features and the other containing Labels .
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.separate_label_feature.__name__,
            __file__,
            self.log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.X = data.drop(labels=label_column_name, axis=1)

            self.Y = data[label_column_name]

            self.log_writer.log(f"Separated {label_column_name} from {data}", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return self.X, self.Y

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def replace_invalid_values(self, data):
        """
        Method Name :   replace_invalid_values
        Description :   This method replaces the invalid values with np.nan
        
        Output      :   A dataframe without invalid values is returned
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.replace_invalid_values.__name__,
            __file__,
            self.log_file,
        )

        try:
            self.log_writer.start_log("start", **log_dic)

            data.replace(to_replace="'na'", value=np.nan, inplace=True)

            self.log_writer.log("Replaced " "na" " with np.nan", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return data

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def is_null_present(self, data):
        """
        Method Name :   is_null_present
        Description :   This method checks whether there are null values present in the pandas dataframe or not.
        
        Output      :   Returns True if null values are present in the DataFrame, False if they are not present and
                        returns the list of columns for which null values are present.
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.is_null_present.__name__,
            __file__,
            self.log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        self.null_present = False

        self.cols_with_missing_values = []

        self.cols = data.columns

        try:
            self.null_counts = data.isna().sum()

            self.log_writer.log(f"Null values count is : {self.null_counts}", **log_dic)

            for i in range(len(self.null_counts)):
                if self.null_counts[i] > 0:
                    self.null_present = True

                    self.cols_with_missing_values.append(self.cols[i])

            self.log_writer.log("created cols with missing values", **log_dic)

            if self.null_present:
                self.log_writer.log(
                    "null values were found the columns...preparing dataframe with null values",
                    **log_dic,
                )

                self.dataframe_with_null = pd.DataFrame()

                self.dataframe_with_null["columns"] = data.columns

                self.dataframe_with_null["missing values count"] = np.asarray(
                    data.isna().sum()
                )

                self.log_writer.log("Created dataframe with null values", **log_dic)

                self.s3.upload_df_as_csv(
                    self.dataframe_with_null,
                    self.null_values_file,
                    self.null_values_file,
                    self.input_files_bucket,
                    self.log_file,
                )

            else:
                self.log_writer.log(
                    "No null values are present in cols. Skipped the creation of dataframe",
                    **log_dic,
                )

            self.log_writer.start_log("exit", **log_dic)

            return self.null_present

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def encode_target_cols(self, data):
        """
        Method Name :   encode_target_cols
        Description :   This method encodes all the categorical values in the training set.
        
        Output      :   A dataframe which has target values encoded.
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.encode_target_cols.__name__,
            __file__,
            self.log_file,
        )

        try:
            self.log_writer.start_log("start", **log_dic)

            data["class"] = data["class"].map({"'neg'": 0, "'pos'": 1})

            self.log_writer.log("Encoded target cols in dataframe", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return data

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def impute_missing_values(self, data):
        """
        Method Name :   impute_missing_values
        Description :   This method replaces all the missing values in the dataframe using mean values of the column.
        
        Output      :   A dataframe which has all the missing values imputed.
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.impute_missing_values.__name__,
            __file__,
            self.log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        self.data = data

        try:
            imputer = KNNImputer(
                n_neighbors=self.knn_neighbours,
                weights=self.knn_weights,
                missing_values=np.nan,
            )

            self.log_writer.log(f"Initialized {imputer.__class__.__name__}", **log_dic)

            self.new_array = imputer.fit_transform(self.data)

            self.new_data = pd.DataFrame(data=self.new_array, columns=self.data.columns)

            self.log_writer.log("Created new dataframe with imputed values", **log_dic)

            self.log_writer.log("Imputing missing values Successful", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return self.new_data

        except Exception as e:
            raise e

    def apply_pca_transform(self, X_scaled_data):
        """
        Method Name : apply_pca_transform
        Description : This method applies the PCA transformation the features cols
        
        Output      : A dataframe with scaled values
        On Failure  : Write an exception log and then raise an exception

        Version     : 1.2
        Revisions   : moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.apply_pca_transform.__name__,
            __file__,
            self.log_file,
        )

        try:
            self.log_writer.start_log("start", **log_dic)

            pca = PCA(n_components=self.n_components)

            pca_model_name = pca.__class__.__name__

            self.log_writer.log(
                f"Initialized {pca_model_name} model with n_components to {self.n_components}",
                **log_dic,
            )

            new_data = pca.fit_transform(X_scaled_data)

            self.log_writer.log(
                f"Transformed the data using {pca_model_name} model", **log_dic
            )

            principal_x = pd.DataFrame(new_data, index=self.data.index)

            self.log_writer.log(
                "Created a dataframe for the transformed data", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

            return principal_x

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def scale_numerical_columns(self, data):
        """
        Method Name : scale_numerical_columns
        Description : This method scales the numerical values using the Standard scaler.
        
        Output      : A dataframe with scaled values
        On Failure  : Write an exception log and then raise an exception

        Version     : 1.2
        Revisions   : moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.scale_numerical_columns.__name__,
            __file__,
            self.log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.data = data

            self.scaler = StandardScaler()

            self.log_writer.log(
                f"Initialized {self.scaler.__class__.__name__}", **log_dic
            )

            self.scaled_data = self.scaler.fit_transform(self.data)

            self.log_writer.log(
                f"Transformed data using {self.scaler.__class__.__name__}", **log_dic
            )

            self.scaled_num_df = pd.DataFrame(
                data=self.scaled_data, columns=self.data.columns, index=self.data.index
            )

            self.log_writer.log("Converted transformed data to dataframe", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return self.scaled_num_df

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_columns_with_zero_std_deviation(self, data):
        """
        Method Name :   get_columns_with_zero_std_deviation
        Description :   This method finds out the columns which have a standard deviation of zero.
        
        Output      :   List of the columns with standard deviation of zero
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_columns_with_zero_std_deviation.__name__,
            __file__,
            self.log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            data_n = data.describe()

            cols_to_drop = [x for x in data.columns if data_n[x]["std"] == 0]

            self.log_writer.log("Got cols with zero standard deviation", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return cols_to_drop

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def handleImbalance(self, X, Y):
        try:
            sample = SMOTE()

            X_bal, y_bal = sample.fit_resample(X, Y)

            return X_bal, y_bal

        except Exception as e:
            raise e
