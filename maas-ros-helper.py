from flask import Flask,request,json
import jsonify
import routeros_api
import logging
import sys
from logging.handlers import RotatingFileHandler

with open("config.json", 'r') as json_data_file:
    config = json.load(json_data_file)

logDir = config["system"]["log"]
logFile = logDir+config["mikrotik"]["name"]+".log"


class StreamToLogger(object):

   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''

   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

   def flush(self):
      pass

handler = RotatingFileHandler(logFile,"a",maxBytes=1048576,backupCount=5)

logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
   handlers = [ handler ]
)


stdout_logger = logging.getLogger('STDOUT')
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl

stderr_logger = logging.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl

global pstat
pstat = "running"
rosip = config["mikrotik"]["ip"]
rosusn = config["mikrotik"]["username"]
rossec = config["mikrotik"]["password"]
maascert = config["system"]["cert"]
maaskey = config["system"]["key"]
connection = routeros_api.RouterOsApiPool(
   rosip, 
   username=rosusn, 
   password=rossec,
   port=8728,
   use_ssl=False,
   ssl_verify=False,
   ssl_verify_hostname=False,
   plaintext_login=True
)
api = connection.get_api()

def ros_usb_reset():
    api.get_resource('/system/routerboard/usb/').call('power-reset')
    return 'USB Interface Reset'

app = Flask(__name__)
@app.route('/usb-reset', methods=["POST", "GET"])
def pwr_reset():
    usb_pwr=ros_usb_reset()
    global pstat
    pstat = "running"
    return pstat

@app.route('/usb-off', methods=["POST", "GET"])
def pwr_off():
    global pstat
    pstat = "running"
    return pstat

@app.route('/usb-status', methods=["POST", "GET"])
def pwr_status():
    pwr_stat = {"status":pstat}
    return pwr_stat
 
if __name__ == '__main__':
    context = (maascert, maaskey)
    app.run(host='0.0.0.0', port=6437, debug=True, ssl_context=context)

