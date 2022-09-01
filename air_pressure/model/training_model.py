from air_pressure.data_ingestion.data_loader_train import Data_Getter_Train
from air_pressure.data_preprocessing.preprocessing import Preprocessor
from air_pressure.mlflow_utils.mlflow_operations import MLFlow_Operation
from air_pressure.model_finder.tuner import Model_Finder
from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Train_Model:
    """
    Description :   This method is used for getting the data and applying
                    some preprocessing steps and then train the models and register them in mlflow
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.log_writer = App_Logger()

        self.config = read_params()

        self.model_train_log = self.config["log"]["model_training"]

        self.target_col = self.config["target_col"]

        self.mlflow_op = MLFlow_Operation(self.model_train_log)

        self.data_getter_train = Data_Getter_Train(self.model_train_log)

        self.preprocessor = Preprocessor(self.model_train_log)

        self.tuner = Model_Finder(self.model_train_log)

        self.s3 = S3_Operation()

    def training_model(self):
        """
        Method Name :   training_model
        Description :   This method is responsible for applying the preprocessing functions and then train models againist 
                        training data and them register them in mlflow

        Output      :   A pandas series object consisting of runs for the particular experiment id
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.training_model.__name__,
            __file__,
            self.model_train_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            data = self.data_getter_train.get_data()

            data = self.preprocessor.replace_invalid_values(data)

            data = self.preprocessor.encode_target_cols(data)

            is_null_present = self.preprocessor.is_null_present(data)

            if is_null_present:
                data = self.preprocessor.impute_missing_values(data)

            X, Y = self.preprocessor.separate_label_feature(data, self.target_col)

            cols_to_drop = self.preprocessor.get_columns_with_zero_std_deviation(X)

            X = self.preprocessor.remove_columns(X, cols_to_drop)

            X = self.preprocessor.scale_numerical_columns(X)

            X = self.preprocessor.apply_pca_transform(X)

            X, Y = self.preprocessor.handleImbalance(X, Y)

            model_score_lst = self.tuner.train_and_log_models(
                X, Y, self.model_train_log
            )

            self.log_writer.log("Successful End of Training", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return model_score_lst

        except Exception as e:
            self.log_writer.log("Unsuccessful End of Training", **log_dic)

            self.log_writer.exception_log(e, **log_dic)
