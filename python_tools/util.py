import logging
import pandas as pd

from python_tools.constants import *


# We look for the regex class at runtime:
# https://stackoverflow.com/questions/6102019/type-of-compiled-regex-object-in-python
RETYPE = type(re.compile('duct_typing'))


def read_df(f, header=None):
    """
    Helper to read our particular format of metrics files

    Waltz does not use headers, but in some cases we will want to provide header='infer' to this function
    """
    try:
        df = pd.read_csv(f, sep='\t', header=header)
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


def merge_files_across_samples(files, cols, sample_ids=None):
    """
    Helper to merge sample files and add in sample name as a new column
    """
    all_dataframes = []
    for f in files:
        new = read_df(f)
        logging.info(new.head())

        if new.empty:
            pass

        # Attempt to extract sample ID if list of ids provided
        if sample_ids is not None:
            sample_id = extract_sample_name(f, sample_ids)
        else:
            sample_id = f
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


class ArgparseMock():
    """
    Mock class to simply have keys and values that simulate the argparse object for testing purposes
    """
    def __init__(self, args):

        for key, value in zip(args.keys(), args.values()):

            setattr(self, key, value)


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
