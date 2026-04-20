# Google Cloud (GCP)

Read-only access to GCP infrastructure. Use for checking deployments, reading logs, and inspecting configuration.

**Do not run commands that modify resources** (deploy, delete, update, create, patch, set-iam-policy, etc.). Stick to list, describe, and read commands only.

## Key Tool
- **`mcp__gcloud__run_gcloud_command`** — Run a `gcloud` CLI command. Params: `command` (array of args including `gcloud`, e.g. `["gcloud", "run", "services", "list"]`), `project_id` (optional)

## Common Commands

**Deployments and services:**
- `["gcloud", "run", "services", "list", "--region=us-central1"]` — list Cloud Run services
- `["gcloud", "run", "services", "describe", "SERVICE", "--region=us-central1"]` — service details (image, env vars, scaling)
- `["gcloud", "run", "revisions", "list", "--service=SERVICE", "--region=us-central1"]` — deployment history
- `["gcloud", "container", "clusters", "list"]` — list GKE clusters

**Logs:**
- `["gcloud", "logging", "read", "resource.type=cloud_run_revision AND resource.labels.service_name=SERVICE", "--limit=50", "--format=json"]`
- `["gcloud", "logging", "read", "severity>=ERROR AND timestamp>=\"2026-03-30T00:00:00Z\"", "--limit=20"]`

**Cloud Build:**
- `["gcloud", "builds", "list", "--limit=10"]` — recent builds
- `["gcloud", "builds", "describe", "BUILD_ID"]` — build details and logs

**Configuration:**
- `["gcloud", "secrets", "list"]` — list Secret Manager secrets (names only, not values)
- `["gcloud", "sql", "instances", "list"]` — list Cloud SQL instances
- `["gcloud", "compute", "instances", "list"]` — list VMs

## Usage Tips
- Always specify `--region` or `--zone` when required
- Use `--format=json` for structured output you can parse
- Default project is configured via `GOOGLE_CLOUD_PROJECT` env — pass `project_id` to override