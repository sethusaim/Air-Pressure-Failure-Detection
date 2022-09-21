from io import StringIO
from json import loads
from os import listdir
from os import remove as os_remove
from os.path import join
from pickle import dump
from pickle import loads as pickle_loads
from shutil import rmtree

import boto3
import pandas as pd
from botocore.exceptions import ClientError

from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class S3_Operation:
    """
    Description :   This method is used for all the S3 bucket operations
    Written by  :   iNeuron Intelligence
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.log_writer = App_Logger()

        self.config = read_params()

        self.file_format = self.config["save_format"]

        self.s3_client = boto3.client("s3")

        self.s3_resource = boto3.resource("s3")

    def read_object(self, object, log_file, decode=True, make_readable=False):
        """
        Method Name :   read_object
        Description :   This method reads the object with kwargs

        Output      :   A object is read with kwargs
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.read_object.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            func = (
                lambda: object.get()["Body"].read().decode()
                if decode is True
                else object.get()["Body"].read()
            )

            self.log_writer.log(
                f"Read the s3 object with decode as {decode}", **log_dic
            )

            conv_func = lambda: StringIO(func()) if make_readable is True else func()

            self.log_writer.log(
                f"read the s3 object with make_readable as {make_readable}", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

            return conv_func()

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def read_text(self, fname, bucket, log_file):
        """
        Method Name :   read_text
        Description :   This method reads the text data from s3 bucket

        Output      :   Text data is read from s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.read_text.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            txt_obj = self.get_file_object(fname, bucket, log_file)

            content = self.read_object(txt_obj, log_file)

            self.log_writer.log(
                f"Read {fname} file as text from {bucket} bucket", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

            return content

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def read_json(self, fname, bucket, log_file):
        """
        Method Name :   read_json
        Description :   This method reads the json data from s3 bucket

        Output      :   Json data is read from s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.read_json.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            f_obj = self.get_file_object(fname, bucket, log_file)

            json_content = self.read_object(f_obj, log_file)

            dic = loads(json_content)

            self.log_writer.log(f"Read {fname} from {bucket} bucket", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return dic

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_df_from_object(self, object, log_file):
        """
        Method Name :   get_df_from_object
        Description :   This method gets dataframe from object 

        Output      :   Dataframe is read from the object
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_df_from_object.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            content = self.read_object(object, log_file, make_readable=True)

            df = pd.read_csv(content)

            self.log_writer.start_log("exit", **log_dic)

            return df

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def read_csv(self, fname, bucket, log_file):
        """
        Method Name :   read_csv
        Description :   This method reads the csv data from s3 bucket

        Output      :   A pandas series object consisting of runs for the particular experiment id
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.read_csv.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            csv_obj = self.get_file_object(fname, bucket, log_file)

            df = self.get_df_from_object(csv_obj, log_file)

            self.log_writer.log(
                f"Read {fname} csv file from {bucket} bucket", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

            return df

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def read_csv_from_folder(self, folder_name, bucket, log_file):
        """
        Method Name :   read_csv_from_folder
        Description :   This method reads the csv files from folder

        Output      :   A list of tuple of dataframe, along with absolute file name and file name is returned
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.read_csv_from_folder.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)
        try:
            files = self.get_files_from_folder(folder_name, bucket, log_file)

            lst = [
                (self.read_csv(f, bucket, log_file,), f, f.split("/")[-1],)
                for f in files
                if f.endswith(".csv")
            ]

            self.log_writer.log(
                f"Read csv files from {folder_name} folder from {bucket} bucket",
                **log_dic,
            )

            self.log_writer.start_log("exit", **log_dic)

            return lst

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def create_folder(self, folder_name, bucket, log_file):
        """
        Method Name :   create_folder
        Description :   This method creates a folder in s3 bucket

        Output      :   A folder is created in s3 bucket 
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.create_folder.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.s3_resource.Object(bucket, folder_name).load()

            self.log_writer.log(f"Folder {folder_name} already exists.", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                self.log_writer.log(
                    f"{folder_name} folder does not exist,creating new one", **log_dic
                )

                folder_obj = folder_name + "/"

                self.s3_client.put_object(Bucket=bucket, Key=folder_obj)

                self.log_writer.log(
                    f"{folder_name} folder created in {bucket} bucket", **log_dic
                )

            else:
                self.log_writer.log(
                    f"Error occured in creating {folder_name} folder", **log_dic
                )

                self.log_writer.exception_log(e, **log_dic)

    def put_object(self, object, bucket, log_file):
        """
        Method Name :   put_object
        Description :   This method puts an object in s3 bucket

        Output      :   An object is put in s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.put_object.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.s3_client.put_object(bucket, (object + "/"))

            self.log_writer.log(
                f"Created {object} folder in {bucket} bucket", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def upload_file(self, from_fname, to_fname, bucket, log_file, remove=True):
        """
        Method Name :   upload_file
        Description :   This method uploades a file to s3 bucket with kwargs

        Output      :   A file is uploaded to s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.upload_file.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.log_writer.log(
                f"Uploading {from_fname} to s3 bucket {bucket}", **log_dic
            )

            self.s3_resource.meta.client.upload_file(from_fname, bucket, to_fname)

            self.log_writer.log(
                f"Uploaded {from_fname} to s3 bucket {bucket}", **log_dic
            )

            if remove is True:
                self.log_writer.log(
                    f"Option remove is set {remove}..deleting the file", **log_dic
                )

                os_remove(from_fname)

                self.log_writer.log(
                    f"Removed the local copy of {from_fname}", **log_dic
                )

                self.log_writer.start_log("exit", **log_dic)

            else:
                self.log_writer.log(
                    f"Option remove is set {remove}, not deleting the file", **log_dic
                )

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_bucket(self, bucket, log_file):
        """
        Method Name :   get_bucket
        Description :   This method gets the bucket from s3 

        Output      :   A s3 bucket name is returned based on the bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.get_bucket.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            bucket = self.s3_resource.Bucket(bucket)

            self.log_writer.log(f"Got {bucket} bucket", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return bucket

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def copy_data(self, from_fname, from_bucket, to_fname, to_bucket, log_file):
        """
        Method Name :   copy_data
        Description :   This method copies the data from one bucket to another bucket

        Output      :   The data is copied from one bucket to another
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.copy_data.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            copy_source = {"Bucket": from_bucket, "Key": from_fname}

            self.s3_resource.meta.client.copy(copy_source, to_bucket, to_fname)

            self.log_writer.log(
                f"Copied data from bucket {from_bucket} to bucket {to_bucket}",
                **log_dic,
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def delete_file(self, fname, bucket, log_file):
        """
        Method Name :   delete_file
        Description :   This method delete the file from s3 bucket

        Output      :   The file is deleted from s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.delete_file.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.s3_resource.Object(bucket, fname).delete()

            self.log_writer.log(f"Deleted {fname} from bucket {bucket}", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def move_data(self, from_fname, from_bucket, to_fname, to_bucket, log_file):
        """
        Method Name :   move_data
        Description :   This method moves the data from one bucket to other bucket

        Output      :   The data is moved from one bucket to another
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.move_data.__name__

        log_dic = get_log_dic(
            self.__class__.__name__, self.move_data.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.copy_data(from_fname, from_bucket, to_fname, to_bucket, log_file)

            self.delete_file(from_fname, from_bucket, log_file)

            self.log_writer.log(
                f"Moved {from_fname} from bucket {from_bucket} to {to_bucket}",
                **log_dic,
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_files_from_folder(self, folder_name, bucket, log_file):
        """
        Method Name :   get_files_from_folder
        Description :   This method gets the files a folder in s3 bucket

        Output      :   A list of files is returned
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_files_from_folder.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            lst = self.get_file_object(folder_name, bucket, log_file)

            list_of_files = [object.key for object in lst]

            self.log_writer.log(f"Got list of files from bucket {bucket}", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return list_of_files

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_file_object(self, fname, bucket, log_file):
        """
        Method Name :   get_file_object
        Description :   This method gets the file object from s3 bucket

        Output      :   A file object is returned
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.get_file_object.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            bucket = self.get_bucket(bucket, log_file)

            lst_objs = [object for object in bucket.objects.filter(Prefix=fname)]

            self.log_writer.log(f"Got {fname} from bucket {bucket}", **log_dic)

            func = lambda x: x[0] if len(x) == 1 else x

            file_objs = func(lst_objs)

            self.log_writer.start_log("exit", **log_dic)

            return file_objs

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def load_model(self, model_name, bucket, log_file, model_dir=None):
        """
        Method Name :   load_model
        Description :   This method loads the model from s3 bucket

        Output      :   A pandas series object consisting of runs for the particular experiment id
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.load_model.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            func = (
                lambda: model_name + self.file_format
                if model_dir is None
                else model_dir + "/" + model_name + self.file_format
            )

            model_file = func()

            self.log_writer.log(f"Got {model_file} as model file", **log_dic)

            f_obj = self.get_file_object(model_file, bucket, log_file)

            model_obj = self.read_object(f_obj, log_file, decode=False)

            model = pickle_loads(model_obj)

            self.log_writer.log(f"Loaded {model_name} from bucket {bucket}", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return model

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def save_model(self, model, model_dir, model_bucket, log_file, idx=None):
        """
        Method Name :   save_model
        Description :   This method saves the model into particular model directory in s3 bucket with kwargs

        Output      :   A pandas series object consisting of runs for the particular experiment id
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.save_model.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            model_name = model.__class__.__name__

            model_file = model_name + self.file_format

            with open(file=model_file, mode="wb") as f:
                dump(model, f)

            self.log_writer.log(
                f"Saved {model_name} model as {model_file} name", **log_dic
            )

            bucket_model_path = model_dir + "/" + model_file

            self.log_writer.log(
                f"Uploading {model_file} to {model_bucket} bucket", **log_dic
            )

            self.upload_file(
                model_file, bucket_model_path, model_bucket, log_file,
            )

            self.log_writer.log(
                f"Uploaded  {model_file} to {model_bucket} bucket", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.log(
                f"Model file {model_name} could not be saved", **log_dic
            )

            self.log_writer.exception_log(e, **log_dic)

    def upload_df_as_csv(self, data_frame, local_fname, bucket_fname, bucket, log_file):
        """
        Method Name :   upload_df_as_csv
        Description :   This method uploades a dataframe as csv file to s3 bucket

        Output      :   A dataframe is uploaded as csv file to s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.upload_df_as_csv.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            data_frame.to_csv(local_fname, index=None, header=True)

            self.log_writer.log(
                f"Created a local copy of dataframe with name {local_fname}", **log_dic
            )

            self.upload_file(
                local_fname, bucket_fname, bucket, log_file,
            )

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def upload_folder(self, folder, bucket, log_file, remove_folder=True):
        """
        Method Name :   upload_folder
        Description :   This method uploades a uploades folder to s3 bucket
        
        Output      :   Folder is uploaded to s3 bucket
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.upload_folder.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            lst = listdir(folder)

            self.log_writer.log("Got a list of files from folder", **log_dic)

            for f in lst:
                local_f = join(folder, f)

                dest_f = folder + "/" + f

                self.upload_file(
                    local_f, dest_f, bucket, log_dic["log_file"], remove=False
                )

            self.log_writer.log("Uploaded folder to s3 bucket", **log_dic)

            if remove_folder is True:
                rmtree(folder)

            else:
                pass

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)
