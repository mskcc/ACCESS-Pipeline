import re
import logging
import pandas as pd

from constants import *


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
    """
    sample_names = [s.split('_IGO')[0] for s in sample_names]
    sample_names = sorted(sample_names, key=len, reverse=True)
    sample_name_search = r'|'.join(sample_names)
    sample_name_search = r'.*(' + sample_name_search + ').*'
    return re.sub(sample_name_search, r'\1', has_a_sample)


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
    :param list: elements to find substring in
    :return: True / False if found / not found
    """

    for elem in list:
        if type(substring) == str:
            if substring in elem:
                return True
        elif type(substring) == RETYPE:
            if substring.match(elem):
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
        if tofind.split('_IGO')[0] in e:
            return i
