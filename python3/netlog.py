import time, os

def get_extra(txt):
    return ""

time_format = "%y%m%d %T"
log_date_format = "%y%m%d"

log_files = []

def log(text):
    txt = " ["+time.strftime(time_format)+"] "+get_extra(text)+" "+text+'\n'
    print(txt, end='')
    for i in log_files:
        if i:
            i.write(txt)
            i.flush()
def add_log_file(filename):
    if filename.find('{}')!=-1:
        filename = filename.format(time.strftime(log_date_format))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    log_files.append(open(filename, 'a+'))
