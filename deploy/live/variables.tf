variable "environment" {
  type        = string
  description = "Lifecycle Environment"
  validation {
    condition     = length(var.environment) < 4
    error_message = "The environment variable must be less 4 characters."
  }
}

variable "tags" {
  type        = map(string)
  description = "Common tags to apply to all resources"
  default     = {}
}

variable "region" {
  type        = string
  description = "AWS Region"
}

variable "revision" {
  type        = number
  description = "Revision Number"
  default     = 1
}

variable "sourcehub-app-version" {
  type        = string
  description = "Version tag of the SourceHub app container"
  default     = "latest"
}

variable "sourcehub-scrapeworker-version" {
  type = string
  description = "Version tag of the SourceHub scrapeworker container"
  default = "latest"
}

variable "sourcehub-parseworker-version" {
  type = string
  description = "Version tag of the SourceHub parseworker container"
  default = "latest"
}