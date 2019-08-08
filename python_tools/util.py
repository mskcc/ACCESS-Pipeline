import sys
import logging
import subprocess
import ruamel.yaml
import numpy as np
import pandas as pd

from python_tools.constants import *


# Set up logging
FORMAT = '%(asctime)-15s %(funcName)-8s %(levelname)s %(message)s'

out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setLevel(logging.INFO)
out_hdlr.setFormatter(logging.Formatter(FORMAT))

logger = logging.getLogger('util')
logger.addHandler(out_hdlr)
logger.setLevel(logging.INFO)


# We look for the regex class at runtime:
# https://stackoverflow.com/questions/6102019/type-of-compiled-regex-object-in-python
RETYPE = type(re.compile('duct_typing'))


def read_df(f, header=None, **kwargs):
    """
    Helper to read our particular format of metrics files

    Waltz does not use headers, but in some cases we will want to provide header='infer' to this function

    :param f: file path to read
    :param header: optional header column names
    :param **kwargs: keyword args to be passed to pd.read_csv()
    """
    try:
        df = pd.read_csv(f, sep='\t', header=header, **kwargs)
        return df
    except Exception as e:
        logging.error('Exception reading data file {}: {}'.format(f, e))
        logging.error('Continuing anyways, some metrics may not be available.')
        return pd.DataFrame({})


def to_csv(df, filename):
    """
    Helper to write in desired csv format
    """
    df.to_csv(filename, sep='\t', index=False)


def extract_sample_name(has_a_sample, sample_names):
    """
    Useful for matching sample names in larger strings such as fastq file names.

    Note that we must sort the samples names by length in order to return the longest match:
    e.g. sample_abc123-IGO-XXX, [sample_abc123, sample_abc12] --> sample_abc123

    :param: has_a_sample String that has a Sample ID inside (usually a file path)
    :param: sample_names String[] that contains all possible sample IDs to be found in `has_a_sample`
            Note that if the target sample ID is not in this list, the wrong sample ID may be returned.
    """
    sample_names = sorted(sample_names, key=len, reverse=True)
    sample_name_search = r'|'.join(sample_names)
    sample_name_search = r'.*(' + sample_name_search + ').*'
    return re.sub(sample_name_search, r'\1', has_a_sample)


def two_strings_are_substrings(string1, string2):
    """
    Check if either `string1` or `string2` is a substring of its partner.
    Useful for checking if one Sample ID is a substring of another Sample ID or vice versa

    :param string1: str
    :param string2: str
    :return:
    """
    return (string1 in string2) or (string2 in string1)


def all_strings_are_substrings(strings):
    """
    Returns True if each string in `strings` is either a substring of or has a substring in one of the other strings

    Useful for determining if a group of sample IDs that were found in a fastq file's path should be represented by
    just a single one of the matches (the longest one), or whether there are two different matches, which would be incorrect.

    :param strings: String[]
    :return: True | False
    """
    return all([
        any([
            two_strings_are_substrings(s1, s2) for s2 in strings[i + 1 :]
        ]) for i, s1 in enumerate(strings[ : len(strings) - 1])
    ])


def merge_files_across_samples(files, cols, sample_ids=None, **kwargs):
    """
    Helper to merge sample files and add in sample name as a new column
    """
    all_dataframes = []
    for f in files:
        new = read_df(f, **kwargs)
        logging.info(new.head())

        if new.empty:
            pass

        # Attempt to extract sample ID if list of ids provided
        if sample_ids is not None:
            sample_id = extract_sample_name(f, sample_ids)
        else:
            sample_id = extract_sample_id_from_bam_path(f)
        new.insert(0, SAMPLE_ID_COLUMN, sample_id)

        all_dataframes.append(new)

    final = pd.concat(all_dataframes)

    if final.empty:
        return pd.DataFrame(columns=cols)

    return final


def substring_in_list(substring, list):
    """
    Look for `substring` in each element in `list`

    :param substring: str or compiled regex object - the substring to look for
    :param list: str[] - elements to find substring in
    :return: True / False if found / not found
    """
    for elem in list:
        if type(substring) == str:
            if substring in elem:
                return True
        elif type(substring) == RETYPE:
            if substring.search(elem):
                return True
    return False


def substrings_in_list(substrings, list):
    """
    Check to see that all elements from `substrings` can be found together in a single element of `list`

    :param: substrings List of strings or regex literals
    :param: list List of elements to search through
    :return: True / False if all elements found / not found in single element from `list`
    """
    for elem in list:
        founds = []
        for substring in substrings:
            if type(substring) == str:
                founds.append(substring in elem)
            elif type(substring) == RETYPE:
                if substring.match(elem):
                    founds.append(True)
        if all(founds):
            return True
    return False


def get_position_by_substring(tofind, list):
    '''
    Get index where `tofind` is a substring of the entry of `list`

    :param tofind: string to find in each element of `list`
    :param list: list to search through
    :return: index in `list` where `tofind` is found as a substring
    '''
    for i, e in enumerate(list):
        if tofind in e:
            return i


def reverse_complement(sequence):
    """
    Revcomp the `sequence`

    :return:
    """
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    return "".join(complement.get(base) for base in reversed(sequence))


def autolabel(bars, plt, text_format='%.5f'):
    """
    Attach a text label above each bar displaying its height

    :param bars: matplotlib.container from matplotlib.pyplot.bar
    :param plt: matplotlib.pyplot with bars to annotate
    """
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.,
            1.05 * height,
            text_format % height,
            ha='center',
            va='bottom',
            fontsize=5
        )


def listdir(path, dirname):
    """
    List the contents of `dirname` folder, under `path`.

    :param path:
    :param dirname:
    :return:
    """
    return os.listdir(os.path.join(path, dirname))


def extract_sample_id_from_bam_path(bam_path):
    """
    ACCESS-specific bams will have their sample IDs followed by _cl_aln...

    :param path:
    :return:
    """
    return bam_path.split('/')[-1].split('_cl_aln')[0]


def include_version_info(fh):
    """
    Todo: Include indentifier to indicate if commit == tag
    """
    import version
    fh.write(INPUTS_FILE_DELIMITER)
    fh.write('version: {} \n'.format(version.most_recent_tag))
    fh.write('# Pipeline Run Version Information: \n')
    fh.write('# Version: {} \n'.format(version.version))
    fh.write('# Short Version: {} \n'.format(version.short_version))
    fh.write('# Most Recent Tag: {} \n'.format(version.most_recent_tag))
    fh.write('# Dirty? {} \n'.format(str(version.dirty)))


def find_bams_in_directory(dir):
    """
    Filter to just bam files found in `dir`

    :param dir: string - directory to be searched
    :return:
    """
    files_found = os.listdir(dir)
    bams_found = [os.path.join(dir, f) for f in files_found if BAM_REGEX.match(f)]
    return bams_found


def create_yaml_file_objects(bam_paths):
    """
    Turn a list of paths into a list of cwl-compatible and ruamel-compatible file objects.

    Additionally, sort the files in lexicographical order.

    :param bam_names: file basenames
    :param folder: file folder
    :return:
    """
    return [{'class': 'File', 'path': b} for b in bam_paths]


def substitute_project_root(yaml_file):
    """
    Substitute in the ROOT_PATH variable based on our current installation directory

    The purpose of this method is to support referencing resources in the resources folder

    :param: yaml_file A yaml file read in by ruamel's round_trip_load() method
    """
    for key in yaml_file.keys():
        current_key = yaml_file[key]
        # If we are dealing with a File object
        if isinstance(current_key, ruamel.yaml.comments.CommentedMap) and 'class' in current_key and current_key['class'] == 'File':
            new_value = yaml_file[key]['path'].replace(PIPELINE_ROOT_PLACEHOLDER, ROOT_DIR)
            yaml_file[key]['path'] = new_value

        # If we are dealing with a string
        # Todo: these should be replaced with File types
        if type(yaml_file[key]) == str:
            new_value = yaml_file[key].replace(PIPELINE_ROOT_PLACEHOLDER, ROOT_DIR)
            yaml_file[key] = new_value

    return yaml_file


def include_yaml_resources(fh, yaml_resources_path):
    """
    Insert yaml file contents into yaml file referenced by `fh` file handle.

    Additionally substitute the root directory for the pipeline installation

    :param: fh File Handle to the inputs file for the pipeline
    :param: file_resources_path String representing full path to our resources file
    """
    with open(yaml_resources_path, 'r') as stream:
        resources = ruamel.yaml.round_trip_load(stream)
        resources = substitute_project_root(resources)

    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(resources))


class ArgparseMock():
    """
    Mock class to simply have keys and values that simulate the argparse object for testing purposes
    """
    def __init__(self, args):

        for key, value in zip(args.keys(), args.values()):

            setattr(self, key, value)


def check_multiple_sample_id_matches(title_file, boolv, sample_object):
    """
    If we found multiple matching sample IDs in the path to a fastq, check that one is the "most correct" one, and
    issue a warning to the user.

    :param title_file: pandas.DataFrame with all sample data
    :param boolv: boolean array indicating which title_file Sample IDs were found in our `fastq_object`
    :return:
    :raise Exception: if there is more than one matching sample ID for this fastq file, and they are not substrings of
                        one another
    """
    boolv = boolv.astype(bool)
    matching_sample_ids = title_file[boolv][MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN]

    if all_strings_are_substrings(matching_sample_ids):
        print(DELIMITER + 'WARNING: There are two or more sample ids found in this sample\'s path: {}'.format(
            sample_object))

        print('Here are the suspicious sample IDs:')
        print(matching_sample_ids)

        print('We will choose the longest matching sample ID for this fastq, ' +
                'but please check that it is ordered with the correct RG_ID in the final inputs file.')

        longest_match = max(matching_sample_ids, key=len)
        return np.argmax(title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN] == longest_match)

    else:
        raise Exception('More than one unique sample ID matches fastq {}, exiting.'.format(sample_object['path']))


def get_pos(title_file, sample_object, use_cmo_sample_id=False):
    """
    Return position of `fastq_object` in the Sample ID column of `title_file`

    Used for sorting the entries in the inputs file so that Scatter steps will pair the correct files

    :param: title_file pandas.DataFrame with all required title_file columns (see constants.py)
    :param: sample_object dict with `class`: `File` and `path`: string as read in by ruamel.round_trip_load()
    :param use_cmo_sample_id: Whether to use the use_cmo_sample_id column instead of investigator_sample_id
    :raise Exception: if more than one sample ID in the `title_file` matches this fastq file, or if no sample ID's
            in the `title_file` match this fastq file
    """
    def contained_in(sample_id, fastq):
        """
        Helper method to sort list of fastqs.
        Returns 1 if `sample_id` contained in `fastq`'s path, 0 otherwise
        """
        found = sample_id in fastq['path']

        if found:
            return 1
        else:
            return 0

    if use_cmo_sample_id:
        boolv = title_file[MANIFEST__CMO_SAMPLE_ID_COLUMN].apply(contained_in, fastq=sample_object)
    else:
        # Samples from IGO will use the COLLAB_ID
        boolv = title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN].apply(contained_in, fastq=sample_object)

    if np.sum(boolv) > 1:
        return check_multiple_sample_id_matches(title_file, boolv, sample_object)

    # If there are no matches, throw error
    if np.sum(boolv) < 1:
        err_string = DELIMITER + 'Error, matching sample ID for file {} not found in title file'
        print >> sys.stderr, err_string.format(sample_object)
        raise Exception('Please double check the order of the fastqs in the final inputs.yaml file')

    pos = np.argmax(boolv)
    return pos
