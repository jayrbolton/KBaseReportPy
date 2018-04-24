# -*- coding: utf-8 -*-
import os

"""
Utilities for validating and uploading files
We use an instance of DataFileUtil throughout this module
"""


def fetch_or_upload_files(dfu, files, zip_dir=False):
    """
    Given a list of dictionaries of files that each have either 'path' or 'shock_id'
    Return a list of file dicts that can be passed as 'html_links' or 'file_links' in the report
    :param dfu: DataFileUtil client instance
    :param files: list of file dictionaries (having the File type from the KIDL spec)
    :returns: list of file dictionaries that that can be uploaded to the workspace for the report
    """
    out_files = []
    for each_file in files:
        if 'path' in each_file:
            # Having a 'path' key means we have to upload to shock
            shock = dfu.file_to_shock({
                'file_path': each_file['path'],
                'make_handle': 1,
                'pack': 'zip' if zip_dir else None
            })
        elif 'shock_id' in each_file:
            # Having a 'shock_id' means it is already uploaded
            shock = dfu.own_shock_node({'shock_id': each_file['shock_id'], 'make_handle': 1})
        out_files.append({
            'handle': shock['handle']['hid'],
            'description': each_file.get('description', ''),
            'name': each_file.get('name', ''),
            'label': each_file.get('label', ''),
            'URL': shock['handle']['url'] + '/node/' + shock['handle']['id']
        })
    return out_files


def validate_paths(name, files):
    """
    Raise an exception if any `path` value in `files` is non-existent
    """
    for each_file in files:
        if ('path' in each_file) and (not _file_or_dir(each_file['path'])):
            raise ValueError(
                'File path does not exist: ' + each_file['path']
                + ' . Make sure the file exists in your scratch directory.'
            )


def _file_or_dir(path):
    return os.path.isfile(path) or os.path.isdir(path)
