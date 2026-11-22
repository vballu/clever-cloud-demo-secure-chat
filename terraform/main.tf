# Deploys the secure chat demo on Clever Cloud with Terraform or OpenTofu:
# a Python application with auto-scaling, linked to a PostgreSQL database.
# Keycloak is set up separately (see the README of the repository).

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    clevercloud = {
      source  = "CleverCloud/clevercloud"
      version = ">= 1.2.0"
    }
  }
}

variable "organisation" {
  description = "Clever Cloud organisation ID (orga_...) or personal space (user_...)."
  type        = string
}

variable "region" {
  description = "Region slug, for example par (Paris) or mtl (Montreal)."
  type        = string
  default     = "par"
}

variable "secret_key" {
  description = "Flask secret key, for example the output of `openssl rand -hex 32`."
  type        = string
  sensitive   = true
}

provider "clevercloud" {
  organisation = var.organisation
}

resource "clevercloud_postgresql" "database" {
  name    = "secure-chat-db"
  region  = var.region
  plan    = "xs_sml"
  version = "17"
}

resource "clevercloud_python" "app" {
  name   = "secure-chat"
  region = var.region

  min_instance_count = 1
  max_instance_count = 3
  smallest_flavor    = "S"
  biggest_flavor     = "S"

  dependencies = [clevercloud_postgresql.database.id]

  deployment {
    repository = "https://github.com/vballu/clever-cloud-demo-secure-chat"
  }

  python_version = "3.13"
  module         = "main:app"

  environment = {
    SECRET_KEY = var.secret_key
  }
}
