from flask import Flask,request,json
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


rosip = config["mikrotik"]["ip"]
rosusn = config["mikrotik"]["username"]
rossec = config["mikrotik"]["password"]
connection = routeros_api.RouterOsApiPool(
   rosip, 
   username=rosusn, 
   password=rossec, 
   plaintext_login=True
)
api = connection.get_api()

def ros_usb_reset():
    api.get_resource('/system/routerboard/usb/').call('power-reset')
    return 'USB Interface Reset'

app = Flask(__name__)
@app.route('/usb-reset', methods=["POST"])
def pwr_reset():
    usb_pwr=ros_usb_reset()
    return "{'status':'runninng'}"

@app.route('/usb-off')
def pwr_off():
    return "{'status':'stopped'}"

@app.route('/usb-status')
def pwr_status():
    return "{'status':'runninng'}"
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6437, debug=True)
