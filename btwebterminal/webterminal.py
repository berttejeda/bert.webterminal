import tornado.web
import tornado.ioloop
from btwebterminal.spyder_terminal.server.common import create_app

from btwebterminal.logger import Logger
logger = Logger().init_logger(None)

class WebTerminal:

    def __init__(self):
      pass

    def start(self, host, port, shell='/bin/bash', debug=False):
        logger.info(f'Server is now at: {host}:{port}')
        logger.info(f'Shell: {shell}')
        application = create_app(shell,
                                 debug=debug,
                                 serve_traceback=debug,
                                 autoreload=debug)
        ioloop = tornado.ioloop.IOLoop.instance()
        application.listen(port, address=host)
        try:
            ioloop.start()
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Closing server...\n")
            application.term_manager.shutdown()
            tornado.ioloop.IOLoop.instance().stop()

