terraform {
  backend "s3" {
    bucket = "air-pressure-tf-state"
    key    = "tf_state"
    region = "us-east-1"
  }
}

module "logs_bucket" {
  source = "./s3_buckets/air_pressure_logs_bucket"
}

module "io_files_bucket" {
  source = "./s3_buckets/air_pressure_io_files_bucket"
}

module "feature_store_bucket" {
  source = "./s3_buckets/air_pressure_feature_store"
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
