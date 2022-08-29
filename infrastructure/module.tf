terraform {
  backend "s3" {
    bucket = "air-pressure-tf-state"
    key    = "tf_state"
    region = "us-east-1"
  }
}

module "mongodb_database" {
  source = "./database"
}

module "ecr_repo" {
  source = "./air_pressure_ecr"
}

module "io_files_bucket" {
  source = "./s3_buckets/air_pressure_io_files_bucket"
}

module "mlflow_bucket" {
  source = "./s3_buckets/air_pressure_mlflow_bucket"
}

module "model_bucket" {
  source = "./s3_buckets/air_pressure_model_bucket"
}

module "pred_data_bucket" {
  source = "./s3_buckets/air_pressure_pred_data_bucket"
}

module "raw_data_bucket" {
  source = "./s3_buckets/air_pressure_raw_data_bucket"
}

module "train_data_bucket" {
  source = "./s3_buckets/air_pressure_train_data_bucket"
}