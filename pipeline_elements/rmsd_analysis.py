"""Basic RMSD analysis of a file of docked poses"""
import re

from pipeline_elements import PipelineElement


class RmsdAnalysis(PipelineElement):
    """Basic RMSD analysis of a file of docked poses"""

    def __init__(self, docked_poses):
        """Basic RMSD analysis of a file of docked poses

        :param docked_poses: file of poses from a docking
        """
        self.docked_poses = docked_poses
        self.top_rmsd_s = None
        self.top_rmsd_h = None
        self.top_rmsd_m = None
        self.top_rmsd = None

    def run(self, _recalc=False):
        """Run RMSD analysis"""
        PipelineElement._files_must_exist([self.docked_poses])
        with open(self.docked_poses) as poses_file:
            in_header = False
            for line in poses_file.readlines():
                if '##########' in line and not in_header:
                    in_header = True
                if in_header:
                    if 'HA_RMSDs' in line:
                        self.top_rmsd_s = self.__parse_value(line)
                    if 'HA_RMSDh' in line:
                        self.top_rmsd_h = self.__parse_value(line)
                    if 'HA_RMSDm' in line:
                        self.top_rmsd_m = self.__parse_value(line)
                    if '##########' not in line:
                        break  # only extracting top pose RMSD at the moment

        # prefer rmsd_h > rmsd_s > rmsd_m
        self.top_rmsd = self.top_rmsd_h
        if self.top_rmsd_h < 0 and self.top_rmsd_s < 0:
            self.top_rmsd = self.top_rmsd_m
        elif self.top_rmsd_h < 0:
            self.top_rmsd = self.top_rmsd_s
        return self

    @staticmethod
    def __parse_value(line):
        stripped_line = re.sub(r'\s+', ' ', line)
        _sentinel, _label, value = [x for x in stripped_line.split(' ') if x.strip()]
        return float(value)

    def output_exists(self):
        return all([self.top_rmsd_s, self.top_rmsd_h, self.top_rmsd_m, self.top_rmsd])
