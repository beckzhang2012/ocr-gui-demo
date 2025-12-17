import datetime
import logging
import os

try:
    import termcolor
except Exception:
    termcolor = None

if os.name == "nt":  # Windows
    try:
        import colorama
        colorama.init()
    except Exception:
        pass

from . import __appname__


COLORS = {
    "WARNING": "yellow",
    "INFO": "white",
    "DEBUG": "blue",
    "CRITICAL": "red",
    "ERROR": "red",
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt, use_color=True):
        logging.Formatter.__init__(self, fmt)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS and termcolor is not None:

            def colored(text, color):
                try:
                    return termcolor.colored(text, color=color, attrs=["bold"])
                except Exception:
                    return str(text)

            record.levelname2 = colored("{:<7}".format(record.levelname), COLORS[levelname])
            record.message2 = colored(record.msg, COLORS[levelname])

            asctime2 = datetime.datetime.fromtimestamp(record.created)
            record.asctime2 = (termcolor.colored(asctime2, color="green")
                               if termcolor is not None
                               else str(asctime2))

            record.module2 = (termcolor.colored(record.module, color="cyan")
                              if termcolor is not None
                              else record.module)
            record.funcName2 = (termcolor.colored(record.funcName, color="cyan")
                                if termcolor is not None
                                else record.funcName)
            record.lineno2 = (termcolor.colored(record.lineno, color="cyan")
                              if termcolor is not None
                              else record.lineno)
        else:
            record.levelname2 = "{:<7}".format(record.levelname)
            record.message2 = record.msg
            asctime2 = datetime.datetime.fromtimestamp(record.created)
            record.asctime2 = str(asctime2)
            record.module2 = record.module
            record.funcName2 = record.funcName
            record.lineno2 = record.lineno
        return logging.Formatter.format(self, record)


class ColoredLogger(logging.Logger):

    FORMAT = (
        "[%(levelname2)s] %(module2)s:%(funcName2)s:%(lineno2)s - %(message2)s"
    )

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.INFO)

        color_formatter = ColoredFormatter(self.FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return


logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger(__appname__)
