"""Common pipeline functionality"""
from abc import ABC, abstractmethod
import logging
import subprocess


# intentionally sparse interface pylint: disable=too-few-public-methods
class PipelineElement(ABC):
    """Pipeline element abstract class"""

    @abstractmethod
    def run(self):
        """Run the pipeline element"""

    @staticmethod
    def _commandline(args, cwd=None, input=None):  # consistency with subprocess pylint: disable=redefined-builtin
        """run a commandline call from a pipeline element with logging"""
        logging.debug('running: %s', ' '.join(args))
        if cwd:
            logging.debug('in: %s', cwd)
        output = subprocess.check_output(args, cwd=cwd, input=input, stderr=subprocess.STDOUT)
        if output:
            logging.debug(output.decode('utf8'))
