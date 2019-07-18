# -*- coding: utf-8 -*-

"""
Wrappers for some loading/saving functionality.

Author: Gertjan van den Burg

"""


import pandas as pd
import warnings
import os

from pandas.errors import ParserWarning

from .detect import Detector
from .dict_read_write import DictReader
from .read import reader
from .utils import get_encoding


def read_as_dicts(filename, dialect=None, verbose=False):
    enc = get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fid:
        if dialect is None:
            dialect = Detector().detect(fid.read(), verbose=verbose)
            fid.seek(0)
        r = DictReader(fid, dialect=dialect)
        for row in r:
            yield row


def read_as_lol(filename, dialect=None, verbose=False):
    """Read a CSV file as a list of lists

    This is a convenience function that reads a CSV file and returns the data 
    as a list of lists (= rows).

    Parameters
    ----------
    filename: str
        Path of the CSV file

    dialect: str, SimpleDialect, or csv.Dialect object
        If the dialect is known, it can be provided here. This function uses 
        the CleverCSV :class:``reader`` object, which supports various dialect 
        types (string, SimpleDialect, or csv.Dialect). If None, the dialect 
        will be detected.

    verbose: bool
        Whether or not to show detection progress.

    Returns
    -------
    rows: list
        Returns rows as a list of lists.

    """
    enc = get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fid:
        if dialect is None:
            dialect = Detector().detect(fid.read(), verbose=verbose)
            fid.seek(0)
        r = reader(fid, dialect)
        return list(r)


def csv2df(filename, *args, **kwargs):
    """ Read a CSV file to a Pandas dataframe

    This function uses CleverCSV to detect the dialect, and then passes this to 
    the ``read_csv`` function in pandas. Additional arguments and keyword 
    arguments are passed to ``read_csv`` as well.

    Parameters
    ----------

    filename: str
        The filename of the CSV file. At the moment, only local files are 
        supported.

    *args:
        Additional arguments for the ``pandas.read_csv`` function.

    **kwargs:
        Additional keyword arguments for the ``pandas.read_csv`` function.

    """
    if not (os.path.exists(filename) and os.path.isfile(filename)):
        raise ValueError("Filename must be a regular file")
    enc = get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fid:
        dialect = Detector().detect(fid.read())
    csv_dialect = dialect.to_csv_dialect()

    # This is used to catch pandas' warnings when a dialect is supplied.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="^Conflicting values for .*",
            category=ParserWarning,
        )
        df = pd.read_csv(filename, *args, dialect=csv_dialect, **kwargs)
    return df