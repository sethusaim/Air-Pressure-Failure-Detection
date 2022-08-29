variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "pred-data" {
  type    = string
  default = "air-pressure-pred-data"
}

variable "aws_account_id" {
  type    = string
  default = "347460842118"
}

variable "force_destroy_bucket" {
  type    = bool
  default = true
}