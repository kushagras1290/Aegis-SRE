# Foundation module intentionally contains no production resources yet.
# Cloud/network/database modules must be introduced per target provider with remote locked state.

locals {
  common_labels = {
    "app.kubernetes.io/part-of"    = "aegis-sre"
    "app.kubernetes.io/managed-by" = "terraform"
    "aegis.io/environment"         = var.environment
  }
}
