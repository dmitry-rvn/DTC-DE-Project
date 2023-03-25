variable "project" {
  description = "GCP Project ID"
}

variable "credentials" {
  description = "Path to credentials json-file"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "EU" // "europe-north1"
  type = string
}

variable "data_lake_bucket" {
  description = "Google Cloud Storage bucket name to be created"
  default = "dshol-dtc-data"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "bq_dataset" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  default = "dtc_crypto_data"
  type = string
}