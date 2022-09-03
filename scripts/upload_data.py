from os.path import join

from boto3 import resource

s3_resource = resource("s3")

def upload_raw_data(bucket):
    try:
        folder = "training_data"
        
        for f in folder:
            from_f = join(folder,f)
            
            dest_f = folder + "/" + f
        
            s3_resource.meta.client.upload_file(from_f, bucket, dest_f)
    
    except Exception as e:
        raise e 
    

def upload_file(file_name,bucket):
    try:
        s3_resource.meta.client.upload_file(file_name, bucket, file_name)
    
    except Exception as e:
        raise e 

## For upload_raw_data function, keep bucket name as "yourname-air-pressure-raw-data" 
## For upload_file function, keep bucket name as "yourname-air-pressure-io-files"

if __name__ == "__main__":
    upload_raw_data(bucket="")
    
    upload_file(file_name="air_pressure_schema_training.json",bucket="")
    
    upload_file(file_name="air_pressure_schema_prediction.json",bucket="")