from air_pressure.mlflow_utils.mlflow_operations import MLFlow_Operation
from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Load_Prod_Model:
    """
    Description :   This class shall be used for loading the production model
    Written by  :   iNeuron Intelligence
    Version     :   1.0
    Revisions   :   None
    """

    def __init__(self):
        self.log_writer = App_Logger()

        self.config = read_params()

        self.model_bucket = self.config["s3_bucket"]["air_pressure_model_bucket"]

        self.load_prod_model_log = self.config["log"]["load_prod_model"]

        self.s3 = S3_Operation()

        self.mlflow_op = MLFlow_Operation(self.load_prod_model_log)

    def load_production_model(self, model_lst):
        """
        Method Name :   load_production_model
        Description :   This method is responsible for moving the models from the trained models dir to
                        prod models dir and stag models dir based on the metrics of the cluster

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.load_production_model.__name__,
            __file__,
            self.load_prod_model_log,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            top_mn_lst = max(model_lst, key=lambda item: item[0])[1]

            self.log_writer.log("Got the top model names", **log_dic)

            results = self.mlflow_op.search_mlflow_models(order="DESC")

            for res in results:
                for mv in res.latest_versions:
                    if mv.name in top_mn_lst:
                        self.mlflow_op.transition_mlflow_model(
                            mv.version,
                            "Production",
                            mv.name,
                            self.model_bucket,
                            self.model_bucket,
                        )

                    else:
                        self.mlflow_op.transition_mlflow_model(
                            mv.version,
                            "Staging",
                            mv.name,
                            self.model_bucket,
                            self.model_bucket,
                        )

            self.log_writer.log(
                "Transitioning of models based on scores successfully done", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)
