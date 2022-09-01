import pandas as pd

from air_pressure.data_ingestion.data_loader_prediction import Data_Getter_Pred
from air_pressure.data_preprocessing.preprocessing import Preprocessor
from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Prediction:
    """
    Description :   This class shall be used for loading the production model

    Version     :   1.2
    Revisions   :   moved to setup to cloud
    """

    def __init__(self):
        self.config = read_params()

        self.pred_log = self.config["log"]["pred_main"]

        self.model_bucket = self.config["s3_bucket"]["air_pressure_model_bucket"]

        self.input_files_bucket = self.config["s3_bucket"]["input_files_bucket"]

        self.prod_model_dir = self.config["model_dir"]["prod"]

        self.pred_output_file = self.config["pred_output_file"]

        self.log_writer = App_Logger()

        self.s3 = S3_Operation()

        self.data_getter_pred = Data_Getter_Pred(self.pred_log)

        self.preprocessor = Preprocessor(self.pred_log)

    def find_correct_model_file(self, cluster_number, bucket, log_file):
        """
        Method Name :   find_correct_model_file
        Description :   This method gets correct model file based on cluster number during prediction
        
        Output      :   A correct model file is found 
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.find_correct_model_file.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            list_of_files = self.s3.get_files_from_folder(
                self.prod_model_dir, bucket, log_file
            )

            for file in list_of_files:
                try:
                    if file.index(str(cluster_number)) != -1:
                        model_name = file

                except:
                    continue

            model_name = model_name.split(".")[0]

            self.log_writer.log(
                f"Got {model_name} from {self.prod_model_dir} folder in {bucket} bucket",
                **log_dic,
            )

            self.log_writer.start_log("exit", **log_dic)

            return model_name

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_prod_model_name(self, folder, bucket, log_file):
        """
        Method Name :   predict_from_model
        Description :   This method is used for loading from prod model dir of s3 bucket and use them for prediction

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_prod_model_name.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            list_of_files = self.s3.get_files_from_folder(folder, bucket, log_file)

            self.log_writer.log(
                f"Got list of files from {folder} folder in {bucket} bucket", **log_dic
            )

            return [
                f.split(".")[0].split("/")[1]
                for f in list_of_files
                if f.endswith(".sav")
            ][0]

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def predict_from_model(self):
        """
        Method Name :   predict_from_model
        Description :   This method is used for loading from prod model dir of s3 bucket and use them for prediction

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.predict_from_model.__name__,
            __file__,
            self.pred_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            data = self.data_getter_pred.get_data()

            data = self.preprocessor.replace_invalid_values(data=data)

            is_null_present = self.preprocessor.is_null_present(data=data)

            if is_null_present:
                data = self.preprocessor.impute_missing_values(data=data)

            cols_to_drop = ["cd_000", "ch_000"]

            X = self.preprocessor.remove_columns(data, cols_to_drop)

            X = self.preprocessor.scale_numerical_columns(data=X)

            X = self.preprocessor.apply_pca_transform(X_scaled_data=X)

            prod_model_name = self.get_prod_model_name(
                self.prod_model_dir, self.model_bucket, self.pred_log
            )

            model = self.s3.load_model(
                prod_model_name,
                self.model_bucket,
                self.pred_log,
                model_dir=self.prod_model_dir,
            )

            result = list(model.predict(X))

            result = pd.DataFrame(result, columns=["Predictions"])

            result["Predictions"] = result["Predictions"].map({0: "neg", 1: "pos"})

            self.s3.upload_df_as_csv(
                result,
                self.pred_output_file,
                self.pred_output_file,
                self.input_files_bucket,
                self.pred_log,
            )

            self.log_writer.log("End of prediction", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return (
                self.input_files_bucket,
                self.pred_output_file,
                result.head().to_json(orient="records"),
            )

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)
