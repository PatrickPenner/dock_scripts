"""Common pipeline functionality"""
from abc import ABC, abstractmethod
import logging
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class PipelineElement(ABC):
    """Pipeline element abstract class"""

    @abstractmethod
    def run(self, recalc=False):
        """Run the pipeline element"""

    @abstractmethod
    def output_exists(self):
        """Pipeline element output exists"""

    @staticmethod
    def _commandline(args, cwd=None, input=None):
        """run a commandline call from a pipeline element with logging"""
        logging.debug('running: %s', ' '.join(args))
        if cwd:
            logging.debug('in: %s', cwd)
        output = subprocess.check_output(args, cwd=cwd, input=input, stderr=subprocess.STDOUT)
        if output:
            logging.debug(output.decode('utf8'))

    @staticmethod
    def _files_must_exist(files):
        """Files exist or exception"""
        if not PipelineElement._files_exist(files):
            raise RuntimeError('Did not find expected files')

    @staticmethod
    def _files_exist(files):
        """Files exist or False"""
        for current_file in files:
            if not os.path.exists(current_file):
                logging.debug('file: %s does not exist', current_file)
                return False
        return True
