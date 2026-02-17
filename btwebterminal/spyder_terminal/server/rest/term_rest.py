# -*- coding: iso-8859-15 -*-

"""Main HTTP routes request handlers."""

import logging
import tornado.web
import tornado.escape
from os import getcwd

LOGGER = logging.getLogger(__name__)


class MainHandler(tornado.web.RequestHandler):
    """Handles creation of new terminals."""

    @tornado.gen.coroutine
    def post(self):
        """POST verb: Create a new terminal."""
        LOGGER.debug("Received POST request to create terminal")
        try:
            rows = int(self.get_argument('rows', default=23))
            cols = int(self.get_argument('cols', default=73))
            cwd = self.get_cookie('cwd', default=getcwd())
            LOGGER.info('Terminal creation request - CWD: {0}, Size: ({1}, {2})'.format(cwd, cols, rows))
            
            LOGGER.debug("Calling term_manager.create_term...")
            pid = yield self.application.term_manager.create_term(rows, cols, cwd)
            LOGGER.info('Terminal created successfully with PID: {0}'.format(pid))
            
            self.write(pid)
        except Exception as e:
            LOGGER.error("Failed to create terminal: {0}".format(str(e)), exc_info=True)
            self.set_status(500)
            self.write({"error": "Failed to create terminal", "details": str(e)})


class ResizeHandler(tornado.web.RequestHandler):
    """Handles resizing of terminals."""

    @tornado.gen.coroutine
    def post(self, pid):
        """POST verb: Resize a terminal."""
        rows = int(self.get_argument('rows', default=23))
        cols = int(self.get_argument('cols', default=73))
        self.application.term_manager.resize_term(pid, rows, cols)
