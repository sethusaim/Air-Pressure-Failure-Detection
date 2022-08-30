import mlflow
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split

from air_pressure.mlflow_utils.mlflow_operations import MLFlow_Operation
from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class Model_Finder:
    """
    Description :   This method is used for hyperparameter tuning of selected models
                    some preprocessing steps and then train the models and register them in mlflow
    Version     :   1.2
    Revisions   :   moved to setup to cloud
    """

    def __init__(self, log_file):
        self.log_file = log_file

        self.config = read_params()

        self.s3 = S3_Operation()

        self.mlflow_op = MLFlow_Operation(log_file)

        self.tuner_kwargs = self.config["model_utils"]

        self.split_kwargs = self.config["base"]

        self.run_name = self.config["mlflow_config"]["run_name"]

        self.train_model_dir = self.config["model_dir"]["trained"]

        self.model_bucket = self.config["s3_bucket"]["air_pressure_model_bucket"]

        self.exp_name = self.config["mlflow_config"]["experiment_name"]

        self.save_format = self.config["save_format"]

        self.log_writer = App_Logger()

        self.ada_model = AdaBoostClassifier()

        self.rf_model = RandomForestClassifier()

    def get_adaboost_model(self, train_x, train_y):
        """
        Method Name :   get_adaboost_model
        Description :   get the parameters for AdaBoost Algorithm which give the best accuracy.
                        Use Hyper Parameter Tuning.
        
        Output      :   The model with the best parameters
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_adaboost_model.__name__,
            __file__,
            self.log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.ada_model_name = self.ada_model.__class__.__name__

            self.adaboost_best_params = self.get_model_params(
                self.ada_model, train_x, train_y, self.log_file
            )

            self.log_writer.log(
                f"{self.ada_model_name} model best params are {self.adaboost_best_params}",
                **log_dic,
            )

            self.ada_model.set_params(**self.adaboost_best_params)

            self.log_writer.log(
                f"Initialized {self.ada_model_name} with {self.adaboost_best_params} as params",
                **log_dic,
            )

            self.ada_model.fit(train_x, train_y)

            self.log_writer.log(
                f"Created {self.ada_model_name} based on the {self.adaboost_best_params} as params",
                **log_dic,
            )

            self.log_writer.start_log("exit", **log_dic)

            return self.ada_model

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_rf_model(self, train_x, train_y):
        """
        Method Name :   get_rf_model
        Description :   get the parameters for Random Forest Algorithm which give the best accuracy.
                        Use Hyper Parameter Tuning.
        
        Output      :   The model with the best parameters
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.get_rf_model.__name__, __file__, self.log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.rf_model_name = self.rf_model.__class__.__name__

            self.rf_best_params = self.get_model_params(
                self.rf_model, train_x, train_y, self.log_file
            )

            self.log_writer.log(
                f"{self.rf_model_name} model best params are {self.rf_best_params}",
                **log_dic,
            )

            self.rf_model.set_params(**self.rf_best_params)

            self.log_writer.log(
                f"Initialized {self.rf_model_name} with {self.rf_best_params} as params",
                **log_dic,
            )

            self.rf_model.fit(train_x, train_y)

            self.log_writer.log(
                f"Created {self.rf_model_name} based on the {self.rf_best_params} as params",
                **log_dic,
            )

            self.log_writer.start_log("exit", **log_dic)

            return self.rf_model

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_model_score(self, model, test_x, test_y, log_file):
        """
        Method Name :   get_model_score
        Description :   This method gets model score againist the test data

        Output      :   A model score is returned 
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.get_model_score.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            model_name = model.__class__.__name__

            preds = model.predict(test_x)

            self.log_writer.log(
                f"Used {model_name} model to get predictions on test data", **log_dic
            )

            if len(test_y.unique()) == 1:
                model_score = accuracy_score(test_y, preds)

                self.log_writer.log(
                    f"Accuracy for {model_name} is {model_score}", **log_dic
                )

            else:
                model_score = roc_auc_score(test_y, preds)

                self.log_writer.log(
                    f"AUC score for {model_name} is {model_score}", **log_dic
                )

            self.log_writer.start_log("exit", **log_dic)

            return model_score

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_model_params(self, model, x_train, y_train, log_file):
        """
        Method Name :   get_model_params
        Description :   This method gets the model parameters based on model_key_name and train data

        Output      :   Best model parameters are returned
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.get_model_params.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            model_name = model.__class__.__name__

            model_param_grid = self.config[model_name]

            model_grid = GridSearchCV(
                estimator=model, param_grid=model_param_grid, **self.tuner_kwargs
            )

            self.log_writer.log(
                f"Initialized {model_grid.__class__.__name__}  with {model_param_grid} as params",
                **log_dic,
            )

            model_grid.fit(x_train, y_train)

            self.log_writer.log(
                f"Found the best params for {model_name} model based on {model_param_grid} as params",
                **log_dic,
            )

            self.log_writer.start_log("exit", **log_dic)

            return model_grid.best_params_

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def train_and_log_models(self, X_data, Y_data, log_file):
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.train_and_log_models.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            x_train, x_test, y_train, y_test = train_test_split(
                X_data, Y_data, **self.split_kwargs
            )

            self.log_writer.log(
                f"Performed train test split with kwargs as {self.split_kwargs}",
                **log_dic,
            )

            model_lst, model_score_lst = self.get_trained_models(
                x_train, y_train, x_test, y_test, log_file
            )

            self.log_writer.log("Got trained models", **log_dic)

            for _, tm in enumerate(model_lst):
                self.s3.save_model(
                    tm[1], self.train_model_dir, self.model_bucket, log_file
                )

                self.mlflow_op.set_mlflow_tracking_uri()

                self.mlflow_op.set_mlflow_experiment(self.exp_name)

                with mlflow.start_run(run_name=self.run_name):
                    self.mlflow_op.log_all_for_model(tm[1], tm[0])

            self.log_writer.log(
                "Saved and logged all trained models to mlflow", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

            return model_score_lst

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_trained_models(self, train_x, train_y, test_x, test_y, log_file):
        """
        Method Name :   get_trained_models
        Description :   Find out the Model which has the best score.
        
        Output      :   The best model name and the model object
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.0
        Revisions   :   None
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_trained_models.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.ada_model = self.get_adaboost_model(train_x=train_x, train_y=train_y)

            self.ada_model_score = self.get_model_score(
                self.ada_model, test_x, test_y, log_file,
            )

            self.rf_model = self.get_rf_model(train_x=train_x, train_y=train_y)

            self.rf_model_score = self.get_model_score(
                self.rf_model, test_x, test_y, log_file,
            )

            self.log_writer.start_log("exit", **log_dic)

            model_lst = [
                (self.rf_model_score, self.rf_model),
                (self.ada_model_score, self.ada_model),
            ]

            model_score_lst = [
                (float(self.rf_model_score), self.rf_model.__class__.__name__),
                (float(self.ada_model_score), self.ada_model.__class__.__name__),
            ]

            return model_lst, model_score_lst

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)
