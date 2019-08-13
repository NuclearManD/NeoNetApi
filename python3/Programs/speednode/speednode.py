import sys, os
sys.path.append(os.path.abspath('../'))

import neonet
import netlog as logging
import filebase, remote_control
import storage, _thread

if not os.path.isfile("cfg.txt"):
    storage.saveDict("cfg.txt", {
        'adr':0xC7860010,
        'key':'default-key',
        'filebase-dir':'./filebase/',
        'log_dir':'./logs/'
        })
cfg = storage.loadDict("cfg.txt")
neonet.setup(cfg['adr'])

logging.add_log_file(os.path.join(cfg['log_dir'],'{}.txt'))

logging.log("Starting Filebase and Remote Control...")
_thread.start_new_thread(filebase.run, (cfg['key'],cfg['filebase-dir']))
_thread.start_new_thread(remote_control.run, (cfg['key'],))
