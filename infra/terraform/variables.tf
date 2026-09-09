variable "environment" {
  description = "Deployment environment name."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of dev, staging, or prod"
  }
}

variable "namespace" {
  description = "Kubernetes namespace for Aegis workloads."
  type        = string
  default     = "aegis-system"
}
