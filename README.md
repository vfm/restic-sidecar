# restic-sidecar

This container provides a web Endpoint to trigger and monitor restic backups.

## Configuration
Configuration is done solely via Environment Variables
|Name|Required|Description|Default|
|---|---|---|---|
| `RSC_LISTEN_ADDRESS` | `false` | Address for the Webserver to listen on | `0.0.0.0` |
| `RSC_LISTEN_PORT` | `false` | Port for the Webserver to listen on  | `9000` |
| `RSC_METRICS_PREFIX` | `false` | Prefix for Metrics | `rsc` |
| `RSC_RETENTION` | `false` | How many daily backups to keep | `1` |
| `RSC_PACKUP_PATHS` | `true` | Comma separated list of paths that should be backed up eg. `/var/lib/data2,/var/lib/data2` | `''` |
| `RSC_BACKUP_KEY` | `true` | Key that is required to trigger Backups | `''` |

## Endpoints
### /metrics
Prints Metrics about Snapshots and Restic Repo statistics in OpenMetricsformat.  
Can be scraped by Prometheus to alert for missing Backups.
### /backup
Requires a `key` Parameter to be set that is identical to `RSC_BACKUP_KEY`, otherwise backups won't be started.  
e.g. 'curl http://localhost:9000/backup?key=mysecret'