from ConfigParser import ConfigParser
from json import *


class AlignerConfig(object):
    config = ConfigParser()

    similarity_threshold = 0

    def __init__(self, language):
        self.config.readfp(open('Config/' + language + '.cfg'))
        self.alignment_similarity_threshold = self.config.getfloat('Aligner', 'alignment_similarity_threshold')
        self.context_similarity_threshold = self.config.getfloat('Aligner', 'context_similarity_threshold')

        self.exact = self.config.getfloat('Aligner', 'exact')
        self.stem = self.config.getfloat('Aligner', 'stem')
        self.synonym = self.config.getfloat('Aligner', 'synonym')
        self.paraphrase = self.config.getfloat('Aligner', 'paraphrase')
        self.related = self.config.getfloat('Aligner', 'related')
        self.related_threshold = self.config.getfloat('Aligner', 'related_threshold')

        self.theta = self.config.getfloat('Aligner', 'theta')


    def get_similar_group(self, pos_source, pos_target, is_opposite, relation):
        group_name = pos_source + '_' + ('opposite_' if is_opposite else '') + pos_target + '_' + relation
        similar_group = []
        for line in self.config.get('Similar Groups', group_name).splitlines():
            similar_group.append(loads(line.strip()))
        return similar_group
