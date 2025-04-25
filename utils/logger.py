"""
Custom logging handlers and filters for Django.

This module contains custom logging handlers that extend the standard
logging handlers with additional functionality like file permissions
and custom rotation behavior, as well as custom filters for log messages.
"""

import os
import stat
import time
from logging import Filter
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class StaticRequestFilter(Filter):
    """Filter that removes log messages containing 'static'."""

    def filter(self, record):
        """Return True if the record should be logged (i.e., if 'static' is not in the message)."""
        return 'static' not in record.getMessage()


class PermissionedRotatingFileHandler(RotatingFileHandler):
    """Custom rotating file handler that sets proper file permissions."""

    def _open(self):
        rtv = super(PermissionedRotatingFileHandler, self)._open()
        os.chmod(self.baseFilename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        return rtv

    def doRollover(self):
        """
        Override the default rotation behavior to use a fixed naming scheme.
        This prevents multiple log files with timestamps from being created.
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # Don't use timestamps in the rotated file names
        # Instead, use a fixed naming scheme with sequential numbers
        for i in range(self.backupCount - 1, 0, -1):
            sfn = f"{self.baseFilename}.{i}"
            dfn = f"{self.baseFilename}.{i + 1}"
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)

        dfn = f"{self.baseFilename}.1"
        if os.path.exists(dfn):
            os.remove(dfn)

        # Rename the base file
        os.rename(self.baseFilename, dfn)

        # Create a new file
        self.mode = 'w'
        self.stream = self._open()


class PermissionedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Custom timed rotating file handler that sets proper file permissions."""

    def _open(self):
        rtv = super(PermissionedTimedRotatingFileHandler, self)._open()
        os.chmod(self.baseFilename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        return rtv

    def doRollover(self):
        """
        Override the default rotation behavior to use a fixed naming scheme.
        This prevents multiple log files with timestamps from being created.
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # Get the time that this sequence started at and make it a TimeTuple
        current_time = int(time.time())

        # Don't use timestamps in the rotated file names
        # Instead, use a fixed naming scheme with sequential numbers
        for i in range(self.backupCount - 1, 0, -1):
            sfn = f"{self.baseFilename}.{i}"
            dfn = f"{self.baseFilename}.{i + 1}"
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)

        dfn = f"{self.baseFilename}.1"
        if os.path.exists(dfn):
            os.remove(dfn)

        # Rename the base file
        os.rename(self.baseFilename, dfn)

        # Create a new file
        self.mode = 'w'
        self.stream = self._open()

        # Set the new rollover time
        self.rolloverAt = self.computeRollover(current_time)
