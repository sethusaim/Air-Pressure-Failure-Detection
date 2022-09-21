from json import loads
from os import environ, makedirs

from pandas import DataFrame
from pymongo import MongoClient

from air_pressure.s3_bucket_operations.s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.read_params import get_log_dic, read_params


class MongoDB_Operation:
    """
    Description :   This method is used for all mongodb operations
    Written by  :   iNeuron Intelligence
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.config = read_params()

        self.DB_URL = environ["MONGODB_URL"]

        self.client = MongoClient(self.DB_URL)

        self.s3 = S3_Operation()

        self.log_writer = App_Logger()

    def get_database(self, db_name, log_file):
        """
        Method Name :   get_database
        Description :   This method gets database from MongoDB from the db_name

        Output      :   A database is created in MongoDB with name as db_name
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.get_database.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            db = self.client[db_name]

            self.log_writer.log(f"Created {db_name} database in MongoDB", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

            return db

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_collection(self, database, collection_name, log_file):
        """
        Method Name :   get_collection
        Description :   This method gets collection from the particular database and collection name

        Output      :   A collection is returned from database with name as collection name
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.get_collection.__name__, __file__, log_file
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            collection = database[collection_name]

            self.log_writer.log(
                f"Created {collection_name} collection in mongodb", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

            return collection

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_collection_as_dataframe(self, db_name, collection_name, log_file):
        """
        Method Name :   get_collection_as_dataframe
        Description :   This method is used for converting the selected collection to dataframe

        Output      :   A collection is returned from the selected db_name and collection_name
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Written by  :   iNeuron Intelligence
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_collection_as_dataframe.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            database = self.get_database(db_name, log_file)

            collection = database.get_collection(name=collection_name)

            df = DataFrame(list(collection.find()))

            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)

            self.log_writer.log("Converted collection to dataframe", **log_dic)

            self.log_writer.start_log("exit", *log_dic)

            return df

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def insert_dataframe_as_record(
        self, data_frame, db_name, collection_name, log_file
    ):
        """
        Method Name :   insert_dataframe_as_record
        Description :   This method inserts the dataframe as record in database collection

        Output      :   The dataframe is inserted in database collection
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.insert_dataframe_as_record.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            records = loads(data_frame.T.to_json()).values()

            self.log_writer.log(f"Converted dataframe to json records", **log_dic)

            database = self.get_database(db_name, log_file)

            collection = database.get_collection(collection_name)

            self.log_writer.log("Inserting records to MongoDB", **log_dic)

            collection.insert_many(records)

            self.log_writer.log("Inserted records to MongoDB", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_collection_names(self, db_name, log_file):
        """
        Method Name :   get_collection_names
        Description :   This method gets the list of collection names from the database

        Output      :   The list of collection names is returned
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_collection_names.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.log_writer.log(
                "Started getting collection names from the database", **log_dic
            )

            db = self.get_database(db_name, log_file)

            lst = db.list_collection_names()

            self.log_writer.log(
                "Got a list of collection names from the database", **log_dic
            )

            self.log_writer.start_log("exit", **log_dic)

            return lst

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def get_collections_as_csv_batch(self, folder_name, db_name, log_file):
        """
        Method Name :   get_collections_as_csv_batch
        Description :   This method gets the collections from the database as csv files 

        Output      :   All the collections present in the database are converted to csv files
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_collections_as_csv_batch.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.log_writer.log("Converting collections to csv files", **log_dic)

            lst = self.get_collection_names(db_name, log_file)

            for collection in lst:
                df = self.get_collection_as_dataframe(db_name, collection, log_file)

                fname = folder_name + "/" + collection + ".csv"

                self.log_writer.log("Got collection as dataframe", **log_dic)

                df.to_csv(fname, index=None, header=True)

                self.log_writer.log(
                    "Converted collection dataframe to csv file", **log_dic
                )

            self.log_writer.log("Converted collections to csv files", **log_dic)

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)

    def transfer_mongo_raw_data_to_s3_bucket(
        self, db_name, folder_name, bucket_name, log_file
    ):
        """
        Method Name :   transfer_mongo_raw_data_to_s3_bucket
        Description :   This method transfers the raw data from mongodb to s3 bucket

        Output      :   Raw data is transferred from mongodb to s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.transfer_mongo_raw_data_to_s3_bucket.__name__,
            __file__,
            log_file,
        )

        self.log_writer.start_log("start", **log_dic)

        try:
            self.log_writer.log(
                "Started transferring files from mongodb to s3 bucket", **log_dic
            )

            makedirs(folder_name, exist_ok=True)

            self.get_collections_as_csv_batch(folder_name, db_name, log_file)

            self.s3.upload_folder(folder_name, bucket_name, log_file)

            self.log_writer.log("Transferred data from mongodb to s3 bucket")

            self.log_writer.start_log("exit", **log_dic)

        except Exception as e:
            self.log_writer.exception_log(e, **log_dic)


    def delete_database(self,db_name,log_file):
        """
        Method Name :   delete_database
        Description :   This method deletes the database from mongodb
        
        Output      :   Database is removed from mongodb
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(self.__class__.__name__,self.delete_database.__name__,__file__,log_file)
        
        self.log_writer.start_log("start",**log_dic)
        
        try:
            self.log_writer.log("Deleting the database from MongoDB",**log_dic)
            
            self.client.drop_database(db_name)
            
            self.log_writer.log("Deleted the database from MongoDB",**log_dic)
            
            self.log_writer.start_log("exit",**log_dic)
        
        except Exception as e:
            self.log_writer.exception_log(e,**log_dic)