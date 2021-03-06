import os.path

from configparser import ConfigParser
from json import *


class AlignerConfig(object):
    config = ConfigParser()

    similarity_threshold = 0
    __similar_groups__ = dict()

    def __init__(self, language):
        self.config.readfp(open(os.path.expanduser('config/aligner/' + language + '.cfg')))
        self.alignment_similarity_threshold = self.config.getfloat('Aligner', 'alignment_similarity_threshold')

        self.exact = self.config.getfloat('Aligner', 'exact')
        self.stem = self.config.getfloat('Aligner', 'stem')
        self.synonym = self.config.getfloat('Aligner', 'synonym')
        self.paraphrase = self.config.getfloat('Aligner', 'paraphrase')
        self.related = self.config.getfloat('Aligner', 'related')
        self.related_threshold = self.config.getfloat('Aligner', 'related_threshold')
        self.selected_lexical_resources = loads(self.config.get('Aligner', 'selected_lexical_resources'))

        self.theta = self.config.getfloat('Aligner', 'theta')

        self.path_to_vectors = self.config.get('Resources', 'vectors')
        self.path_to_ppdb = self.config.get('Resources', 'ppdb')

    def get_similar_group(self, pos_source, pos_target, is_opposite, relation):
        group_name = pos_source + '_' + ('opposite_' if is_opposite else '') + pos_target + '_' + relation

        if group_name in self.__similar_groups__:
            return self.__similar_groups__[group_name]

        similar_group = []
        for line in self.config.get('Similar Groups', group_name).splitlines():
            similar_group.append(loads(line.strip()))

        self.__similar_groups__[group_name] = similar_group

        return similar_group
