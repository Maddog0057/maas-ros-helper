from flask import Flask,request,json
import routeros_api
import logging
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
connection = routeros_api.RouterOsApiPool(rosip, username=rosusn, password=rossec, use_ssl=True)
api = connection.get_api()

def ros_usb_reset(api):
    api.get_resource('/system/routerboard/usb/').call('power-reset')
    return 'USB Interface Reset'

app = Flask(__name__)
@app.route('/usb-reset')
def get_reset():
    ros_usb_reset()
 
if __name__ == '__main__':
    app.run(debug=True)