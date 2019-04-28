import logging


log = logging.getLogger('media-proxy')
log.setLevel(logging.DEBUG)
log.handlers = []
formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] %(message)s')


# Console

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
ch.propagate = False
log.addHandler(ch)
