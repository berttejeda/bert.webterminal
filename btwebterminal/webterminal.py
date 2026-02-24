import os
import tornado.web
import tornado.ioloop
from btwebterminal.spyder_terminal.server.common import create_app
from pathlib import Path

from btwebterminal.logger import Logger
logger = Logger().init_logger(None)

class WebTerminal:

    def __init__(self):
      pass

    def _get_default_shell(self):
        """Get the appropriate shell command for the OS."""
        if os.name == 'nt':  # Windows
            # Try Git Bash first
            localappdata = os.environ.get('LOCALAPPDATA', '')
            git_bash_paths = [
                (Path(localappdata) / "Programs\\Git\\git-cmd.exe"),
                Path("C:\\Program Files\\Git\\git-cmd.exe"),
                Path("C:\\Program Files (x86)\\Git\\git-cmd.exe"),
            ]
            for git_bash in git_bash_paths:
                if git_bash.exists():
                    return [git_bash.as_posix(), "--no-cd", "--command=usr/bin/bash.exe", "-l", "-i"]
            # Fallback to cmd.exe
            return ["cmd.exe"]
        else:
            # Unix-like systems
            return ["/bin/bash"]      

    def start(self, host, port, shell=None, debug=False):
        clr = 'cls'
        webterminal_shell_name = 'bash'
        logger.info(f'Server is now at: {host}:{port}')
        logger.info(f'Shell: {webterminal_shell_name}')
        
        # Use provided shell or detect default
        if shell is None:
            shell = self._get_default_shell()

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
            ioloop.run_sync(application.term_manager.shutdown)
            tornado.ioloop.IOLoop.instance().stop()

