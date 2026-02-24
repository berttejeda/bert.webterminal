# -*- coding: utf-8 -*-

"""Term manager."""
import os
import time
import signal
import hashlib
import shlex
import tornado.web
import tornado.gen
import tornado.ioloop
from terminado.management import TermManagerBase, PtyWithClients
from urllib.parse import unquote

import logging
LOGGER = logging.getLogger(__name__)

WINDOWS = os.name == 'nt'


class PtyReader(PtyWithClients):
    """Wrapper around PtyWithClients."""

    def resize_to_smallest(self, rows, cols):
        """Set the terminal size to that of the smallest client dimensions.

        A terminal not using the full space available is much nicer than a
        terminal trying to use more than the available space, so we keep it
        sized to the smallest client.
        """
        minrows = mincols = 10001
        if rows is not None and rows < minrows:
            minrows = rows
        if cols is not None and cols < mincols:
            mincols = cols

        if minrows == 10001 or mincols == 10001:
            return

        rows, cols = self.ptyproc.getwinsize()
        if (rows, cols) != (minrows, mincols):
            LOGGER.debug("Resizing PTY to {0}x{1}".format(mincols, minrows))
            self.ptyproc.setwinsize(minrows, mincols)


class TermManager(TermManagerBase):
    """Wrapper around pexpect to execute local commands."""

    def __init__(self, shell_command, **kwargs):
        """Create a new terminal handler instance."""
        super().__init__(shell_command, **kwargs)
        self.consoles = {}

    def new_terminal(self, **kwargs):
        """Make a new terminal, return a :class:`PtyReader` instance."""
        options = self.term_settings.copy()
        options['shell_command'] = self.shell_command
        options.update(kwargs)
        argv = options['shell_command']
        
        # Convert list to string for terminado if needed
        if isinstance(argv, list):
            # Flatten and ensure all items are strings
            flat_argv = []
            for item in argv:
                if isinstance(item, list):
                    flat_argv.extend(str(i) for i in item)
                else:
                    flat_argv.append(str(item))
            # Use shlex.quote() for proper shell escaping on Windows
            argv = ' '.join(shlex.quote(arg) for arg in flat_argv)
        
        env = self.make_term_env(**options)
        cwd = options.get('cwd', None)
        LOGGER.debug("Spawning new terminal: {0} in {1}".format(argv, cwd))
        return PtyReader(argv, env, cwd)

    @tornado.gen.coroutine
    def client_disconnected(self, pid, socket):
        """Send terminal SIGHUP when client disconnects."""
        self.log.info("Websocket closed, sending SIGHUP to terminal.")
        term = self.consoles[pid]
        term.clients.remove(socket)
        try:
            if WINDOWS:
                term.kill()
                self.pty_read(term.ptyproc.fd)
                return
            term.killpg(signal.SIGHUP)
        except Exception:
            pass
        del self.consoles[pid]

    @tornado.gen.coroutine
    def create_term(self, rows, cols, cwd=None):
        """Create a new virtual terminal."""
        LOGGER.debug("create_term called with rows={0}, cols={1}, cwd={2}".format(rows, cols, cwd))
        pid = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()[0:6]
        # We need to do percent decoding for reading the cwd through a cookie
        # For further information see spyder-ide/spyder-terminal#225
        cwd = unquote(cwd)
        LOGGER.debug("Decoded CWD: {0}".format(cwd))
        
        try:
            pty = self.new_terminal(cwd=cwd, height=rows, width=cols)
            pty.resize_to_smallest(rows, cols)
            self.consoles[pid] = pty
            LOGGER.info("Terminal created with PID {0} for CWD {1}".format(pid, cwd))
            return pid
        except Exception as e:
            LOGGER.error("Error in TermManager.create_term: {0}".format(str(e)), exc_info=True)
            raise

    @tornado.gen.coroutine
    def start_term(self, pid, socket):
        """Start reading a virtual terminal."""
        term = self.consoles[pid]
        self.start_reading(term)
        term.clients.append(socket)

    @tornado.gen.coroutine
    def execute(self, pid, cmd):
        """Write characters to terminal."""
        term = self.consoles[pid]
        term.ptyproc.write(cmd)

    @tornado.gen.coroutine
    def resize_term(self, pid, rows, cols):
        """Resize terminal."""
        term = self.consoles[pid]
        term.resize_to_smallest(rows, cols)
