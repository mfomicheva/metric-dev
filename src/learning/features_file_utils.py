'''
Created on Aug 29, 2012

@author: desouza
'''
import codecs
import numpy as np
import logging as log
import os
import math
from sklearn.cross_validation import train_test_split

def read_labels_file(path, delim, encoding='utf-8'):
    '''Reads the labels of each column in the training and test files (features 
    and reference files).
    
    @param path: the path of the labels file
    @param delim: the character used to separate the label strings.
    @param encoding: the character encoding used to read the file. 
    Default is 'utf-8'.
    
    @return: a list of strings representing each feature column.
    '''
    labels_file = codecs.open(path, 'r', encoding)
    lines = labels_file.readlines()
    
    if len(lines) > 1:
        log.warn("labels file has more than one line, using the first.")
    
    if len(lines) == 0:
        log.error("labels file is empty: %s" % path)
    
    labels = lines[0].strip().split(delim)
    
    return labels
    
    
def read_reference_file(path, delim, encoding='utf-8', tostring=False):
    """Parses the file that contains the references and stores it in a numpy array.
    
       @param path the path of the file.
       @delim char the character used to separate values.
       
       @return: a numpy array representing each instance response value
    """
    
    # reads the references to a vector
    refs_file = codecs.open(path, 'r', encoding)
    refs_lines = []
    for line in refs_file:
        cols = line.strip().split(delim)
        refs_lines.append(cols[0])

    if tostring:
        refs = np.array(refs_lines, dtype='str')
    else:
        refs = np.asfarray(refs_lines)
    
    return refs


def read_features_file(path, delim, encoding='utf-8', tostring=False):
    '''
    Reads the features for each instance and stores it on an numpy array.
    
    @param path: the path to the file containing the feature set.
    @param delim: the character used to separate the values in the file pointed by path.
    @param encoding: the character encoding used to read the file.
    
    @return: an numpy array where the columns are the features and the rows are the instances.
    '''
    # this method is memory unneficient as all the mtc is kept in memory
    feats_file = codecs.open(path, 'r', encoding='utf-8')
    feats_lines = []
    line_num = 0
    for line in feats_file:
        if line == "":
            continue
        toks = tuple(line.strip().split(delim))
        cols = []
        for t in toks:
            if t != '':
                try:
                    if tostring:
                        cols.append(t)
                    else:
                        cols.append(float(t))
                except ValueError as e:
                    log.error("%s line %s: %s" % (e, line_num, t))
        
        line_num += 1
        feats_lines.append(cols)
    
    #    print feats_lines
    feats = np.asarray(feats_lines)
    
    return feats


def split_dataset(input_path_x, input_path_y, output_dir):

    with open(os.path.expanduser(input_path_x), 'r') as f:
        read_data_x = f.readlines()
    f.close()

    with open(os.path.expanduser(input_path_y), 'r') as f:
        read_data_y = f.readlines()
    f.close()

    x_train, x_test, y_train, y_test = train_test_split(read_data_x, read_data_y)

    write_lines_to_file(output_dir + '/' + 'x_train' + '.' + 'tsv', x_train)
    write_lines_to_file(output_dir + '/' + 'y_train' + '.' + 'tsv', y_train)
    write_lines_to_file(output_dir + '/' + 'x_test' + '.' + 'tsv', x_test)
    write_lines_to_file(output_dir + '/' + 'y_test' + '.' + 'tsv', y_test)


def split_dataset_repeated_segments(input_path_x, input_path_y, output_dir, number_of_segments):

    with open(os.path.expanduser(input_path_x), 'r') as f:
        read_data_x = f.readlines()
    f.close()

    with open(os.path.expanduser(input_path_y), 'r') as f:
        read_data_y = f.readlines()
    f.close()

    segment_numbers = range(0, len(read_data_x))
    number_of_batches = int(len(read_data_x)/number_of_segments)
    train_length = int(round(number_of_segments * 80 / 100))
    test_length = int(round(number_of_segments * 20 / 100))

    x_train = []
    y_train = []
    x_test = []
    y_test = []

    for i in range(number_of_batches):
        print('\n'.join([str(x + 1) for x in segment_numbers[i * number_of_segments + train_length:i * number_of_segments + train_length + test_length]]))
        x_train += read_data_x[i * number_of_segments:i * number_of_segments + train_length]
        y_train += read_data_y[i * number_of_segments:i * number_of_segments + train_length]
        x_test += read_data_x[i * number_of_segments + train_length:i * number_of_segments + train_length + test_length]
        y_test += read_data_y[i * number_of_segments + train_length:i * number_of_segments + train_length + test_length]

    write_lines_to_file(output_dir + '/' + 'x_train' + '.' + 'tsv', x_train)
    write_lines_to_file(output_dir + '/' + 'y_train' + '.' + 'tsv', y_train)
    write_lines_to_file(output_dir + '/' + 'x_test' + '.' + 'tsv', x_test)
    write_lines_to_file(output_dir + '/' + 'y_test' + '.' + 'tsv', y_test)


def write_lines_to_file(file_path, lines):

    with open(os.path.expanduser(file_path), 'w') as f:
        for line in lines:
            f.write(line)
    f.close()

def concatenate_features_files(file_paths):

    feature_arrays = []
    for fp in file_paths:
        feature_arrays.append(read_features_file(fp, "\t"))

    return np.concatenate(feature_arrays, axis=1)

def write_feature_file(output_path, feature_matrix):

    output_file = codecs.open(output_path, 'w', 'utf-8')
    for row in feature_matrix:
        output_file.write('\t'.join([str(x) for x in row]) + '\n')
    output_file.close()

def combine_alignment_files(language_pairs, directory, file_name):

    # Method to combine alignment files for different languages in a single file

    output_file = codecs.open(directory + "/" + "full_dataset" + file_name, "w", "utf-8")

    count = 0

    for language_pair in language_pairs:
        lines = codecs.open(directory + "/" + language_pair + "/" + "we" + "/" + file_name, "r", "utf-8")

        for line in lines:
            if "Sentence #" in line:
                count += 1
                output_file.write("Sentence #" + str(count) + "\n")
            else:
                output_file.write(line)

    output_file.close()


if __name__ == '__main__':

    language_pairs = ["cs-en", "de-en", "fr-en", "hi-en", "ru-en"]

    directory = os.path.expanduser('~/Dropbox/wmt14-alignments')

    file_name = 'tgt.parse.ref.parse.cobalt-align.out'

    combine_alignment_files(language_pairs, directory, file_name)

    pass


