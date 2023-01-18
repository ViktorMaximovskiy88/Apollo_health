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
  type        = string
  description = "Version tag of the SourceHub scrapeworker container"
  default     = "latest"
}

variable "sourcehub-parseworker-version" {
  type        = string
  description = "Version tag of the SourceHub parseworker container"
  default     = "latest"
}

variable "sourcehub-scheduler-version" {
  type        = string
  description = "Version tag of the SourceHub scheduler container"
  default     = "latest"
}

variable "sourcehub-dbmigrations-version" {
  type        = string
  description = "Version tag of the SourceHub db migrations container"
  default     = "latest"
}

variable "sourcehub-taskworker-version" {
  type        = string
  description = "Version tag of the SourceHub taskworker container"
  default     = "latest"
}

variable "sourcehub-taskworker-sync-version" {
  type        = string
  description = "Version tag of the SourceHub taskworker container"
  default     = "latest"
}

variable "auth0-config" {
  type = object({
    domain        = string,
    client_id     = string,
    audience      = string,
    wellknown_url = string,
    issuer        = string,
  })
  description = "Auth0 configuration for SSO"
}
