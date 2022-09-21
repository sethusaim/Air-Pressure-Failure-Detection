resource "aws_s3_bucket" "features_store" {
  bucket        = var.features_store
  force_destroy = var.force_destroy_bucket

}

resource "aws_s3_bucket_versioning" "feature_store_versioning" {
  bucket = aws_s3_bucket.features_store.id
  versioning_configuration {
    status = "Enabled"
  }
}
