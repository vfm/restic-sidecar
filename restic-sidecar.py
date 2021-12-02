import os
import json
import socket
import bottle
import restic
import threading
import dateutil.parser

listen_address = os.environ.get('RSC_LISTEN_ADDRESS','0.0.0.0')
listen_port = os.environ.get('RSC_LISTEN_PORT','9000')
metrics_prefix = os.environ.get('RSC_METRICS_PREFIX','rsc')
retention_policy = os.environ.get('RSC_RETENTION','1')
backup_paths = os.environ.get('RSC_BACKUP_PATHS','')
backup_key = os.environ.get('RSC_BACKUP_KEY', 'bla')

## -- Backup Functions --
def backupCycle(paths,keep_daily):
  response = dict()
  response['backup'] = restic.backup(paths=paths.split(','))
  response['forget'] = restic.forget(prune=True,keep_daily=keep_daily)
  print(json.dumps(response,indent = 2))

## -- Metric Functions --
def formatMetric(name,value,prefix = metrics_prefix,labels = None):
  if labels:
    labelstrings = list()
    for l_key,l_value in labels.items():
      labelstrings.append( l_key + "=\"" + l_value + "\"")
    return str( prefix + "_" + name + "{" + ','.join(labelstrings) + "}: " + str(value))
  else:
    return str( prefix + "_" + name + ": " + str(value) )

def generateMetrics():
  metrics = list()

  # Snapshots
  snaps = restic.snapshots()
  last_snap = snaps[-1]
  metrics.append(formatMetric("last_snapshot_time",dateutil.parser.parse(last_snap['time']).timestamp()))
  metrics.append(formatMetric("last_snapshot_short_id", last_snap['short_id']))
  metrics.append(formatMetric("snapshot_count", sum(i['hostname'] == socket.gethostname() for i in restic.snapshots())))

  # Restore Statistics
  restorestats = restic.stats(mode='restore-size')
  metrics.append(formatMetric("restic_stats_size_bytes", restorestats['total_size'], labels={"type": "restore"}))
  metrics.append(formatMetric("restic_stats_file_count", restorestats['total_file_count'], labels={"type": "restore"}))

  # Raw Repo Statistics
  rawstats = restic.stats(mode='raw-data')
  metrics.append(formatMetric("restic_stats_size_bytes", rawstats['total_size'], labels={"type": "raw"}))
  metrics.append(formatMetric("restic_stats_file_count", rawstats['total_file_count'], labels={"type": "raw"}))

  return metrics

## -- Webserver Setup --
## Setup Webserver
# Index
@bottle.route('/')
def index():
  return """
    <h1>restic backup</h1>
    <ul>
    <li><a href="/metrics">metrics<a/></li>
    <li><a href="/backup">create a backup<a/></li>
    </ul>
  """

# Metrics
@bottle.route('/metrics')
def metrics():
  outputlist = generateMetrics()

  output = str()
  for i in outputlist:
    output += str(i) + "\n"
  
  bottle.response.content_type = 'text/plain'
  return output

# Backup
@bottle.route('/backup')
def backup():
  bottle.response.content_type = 'text/plain'
  key = bottle.request.query.key
  if key and key == backup_key:
    try:
      cycle = threading.Thread(target=backupCycle(backup_paths,retention_policy), name="backupCycle")
      cycle.start()
      bottle.response.status = 200
      return 'Backup Started'
    except Exception as error:
      bottle.response.status = 500
      print(error)
      return 'Error'
  else:
    bottle.response.status = 500
    return 'Unauthorized'

## -- Runtime --
# Init Restic Repo
try:
  restic.init()
except restic.errors.ResticFailedError as e:
  if not str('config file already exists') in str(e):
    raise Exception(e)

# Run Webserver
bottle.run(host=listen_address, port=listen_port)
