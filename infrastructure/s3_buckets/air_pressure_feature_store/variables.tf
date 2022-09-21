variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "features_store" {
  type    = string
  default = "air-pressure-feature-store"
}

variable "aws_account_id" {
  type    = string
  default = "347460842118"
}

variable "force_destroy_bucket" {
  type    = bool
  default = true
}