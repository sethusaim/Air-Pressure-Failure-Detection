import mlflow
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split

from utils.logger import App_Logger
from utils.read_params import read_params


class Model_Finder:
    """
    Description :   This method is used for hyperparameter tuning of selected models
                    some preprocessing steps and then train the models and register them in mlflow
    Version     :   1.2
    Revisions   :   moved to setup to cloud
    """

    def __init__(self, log_file):
        self.log_file = log_file

        self.class_name = self.__class__.__name__

        self.config = read_params()

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
        method_name = self.get_adaboost_model.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, self.log_file,
        )

        try:
            self.ada_model_name = self.ada_model.__class__.__name__

            self.adaboost_best_params = self.get_model_params(
                self.ada_model, train_x, train_y, self.log_file
            )

            self.log_writer.log(
                self.log_file,
                f"{self.ada_model_name} model best params are {self.adaboost_best_params}",
            )

            self.ada_model.set_params(**self.adaboost_best_params)

            self.log_writer.log(
                self.log_file,
                f"Initialized {self.ada_model_name} with {self.adaboost_best_params} as params",
            )

            self.ada_model.fit(train_x, train_y)

            self.log_writer.log(
                self.log_file,
                f"Created {self.ada_model_name} based on the {self.adaboost_best_params} as params",
            )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.log_file,
            )

            return self.ada_model

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.log_file,
            )

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
        method_name = self.get_rf_model.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, self.log_file,
        )

        try:
            self.rf_model_name = self.rf_model.__class__.__name__

            self.rf_best_params = self.get_model_params(
                self.rf_model, train_x, train_y, self.log_file
            )

            self.log_writer.log(
                self.log_file,
                f"{self.rf_model_name} model best params are {self.rf_best_params}",
            )

            self.rf_model.set_params(**self.rf_best_params)

            self.log_writer.log(
                self.log_file,
                f"Initialized {self.rf_model_name} with {self.rf_best_params} as params",
            )

            self.rf_model.fit(train_x, train_y)

            self.log_writer.log(
                self.log_file,
                f"Created {self.rf_model_name} based on the {self.rf_best_params} as params",
            )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.log_file,
            )

            return self.rf_model

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.log_file,
            )

    def get_model_score(self, model, test_x, test_y, log_file):
        """
        Method Name :   get_model_score
        Description :   This method gets model score againist the test data

        Output      :   A model score is returned 
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """

        method_name = self.get_model_score.__name__

        self.log_writer.start_log("start", self.class_name, method_name, log_file)

        try:
            model_name = model.__class__.__name__

            preds = model.predict(test_x)

            self.log_writer.log(
                log_file, f"Used {model_name} model to get predictions on test data"
            )

            if len(test_y.unique()) == 1:
                model_score = accuracy_score(test_y, preds)

                self.log_writer.log(
                    log_file, f"Accuracy for {model_name} is {model_score}"
                )

            else:
                model_score = roc_auc_score(test_y, preds)

                self.log_writer.log(
                    log_file, f"AUC score for {model_name} is {model_score}"
                )

            self.log_writer.start_log("exit", self.class_name, method_name, log_file)

            return model_score

        except Exception as e:
            self.log_writer.exception_log(e, self.class_name, method_name, log_file)

    def get_model_params(self, model, x_train, y_train, log_file):
        """
        Method Name :   get_model_params
        Description :   This method gets the model parameters based on model_key_name and train data

        Output      :   Best model parameters are returned
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """

        method_name = self.get_model_params.__name__

        self.log_writer.start_log("start", self.class_name, method_name, log_file)

        try:
            model_name = model.__class__.__name__

            model_param_grid = self.config[model_name]

            model_grid = GridSearchCV(
                estimator=model, param_grid=model_param_grid, **self.tuner_kwargs
            )

            self.log_writer.log(
                log_file,
                f"Initialized {model_grid.__class__.__name__}  with {model_param_grid} as params",
            )

            model_grid.fit(x_train, y_train)

            self.log_writer.log(
                log_file,
                f"Found the best params for {model_name} model based on {model_param_grid} as params",
            )

            self.log_writer.start_log("exit", self.class_name, method_name, log_file)

            return model_grid.best_params_

        except Exception as e:
            self.log_writer.exception_log(e, self.class_name, method_name, log_file)

    def train_and_log_models(self, X_data, Y_data, log_file, idx=None, kmeans=None):
        method_name = self.train_and_log_models.__name__

        self.log_writer.start_log("start", log_file, self.class_name, method_name)

        try:
            x_train, x_test, y_train, y_test = train_test_split(
                X_data, Y_data, **self.split_kwargs
            )

            self.log_writer.log(
                log_file,
                f"Performed train test split with kwargs as {self.split_kwargs}",
            )

            lst = self.model_finder.get_trained_models(x_train, y_train, x_test, y_test)

            self.log_writer.log(log_file, "Got trained models")

            for _, tm in enumerate(lst):
                self.s3.save_model(
                    tm[0],
                    self.train_model_dir,
                    self.model_bucket,
                    log_file,
                    format=self.save_format,
                )

                self.mlflow_op.set_mlflow_tracking_uri()

                self.mlflow_op.set_mlflow_experiment(self.exp_name)

                with mlflow.start_run(run_name=self.run_name):
                    self.mlflow_op.log_all_for_model(idx, tm[0], tm[1])

                    if kmeans is not None:
                        self.mlflow_op.log_all_for_model(None, kmeans, None)

                    else:
                        pass

            self.log_writer.log(
                log_file, "Saved and logged all trained models to mlflow"
            )

            self.log_writer.start_log("exit", log_file, self.class_name, method_name)

        except Exception as e:
            self.log_writer.exception_log(e, log_file, self.class_name, method_name)

    def get_trained_models(self, train_x, train_y, test_x, test_y, log_file):
        """
        Method Name :   get_trained_models
        Description :   Find out the Model which has the best score.
        
        Output      :   The best model name and the model object
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.0
        Revisions   :   None
        """
        method_name = self.get_trained_models.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, log_file,
        )

        try:
            self.ada_model = self.get_adaboost_model(train_x=train_x, train_y=train_y)

            self.ada_model_score = self.get_model_score(
                self.ada_model, test_x, test_y, log_file,
            )

            self.rf_model = self.get_rf_model(train_x=train_x, train_y=train_y)

            self.rf_model_score = self.get_model_score(
                self.rf_model, test_x, test_y, log_file,
            )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, log_file,
            )

            lst = [
                (self.rf_model, self.rf_model_score),
                (self.ada_model, self.ada_model_score),
            ]

            return lst

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, log_file,
            )
