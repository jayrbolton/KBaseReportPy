# -*- coding: utf-8 -*-
import os

"""
Utilities for validating and uploading files
We use an instance of DataFileUtil throughout this module
"""


def fetch_or_upload_files(dfu, files, zip=False):
    """
    Given a list of dictionaries of files that each have either 'path' or 'shock_id'
    Return a list of file dicts that can be passed as 'html_links' or 'file_links' in the report
    :param dfu: DataFileUtil client instance
    :param files: list of file dictionaries (having the File type from the KIDL spec)
    :returns: list of file dictionaries that that can be uploaded to the workspace for the report
    """
    out_files = []
    for file in files:
        if 'path' in file:
            # Having a 'path' key means we have to upload to shock
            shock = dfu.file_to_shock({
                'file_path': file['path'],
                'make_handle': 1,
                'pack': 'zip' if zip else None
            })
        elif 'shock_id' in file:
            # Having a 'shock_id' means it is already uploaded
            shock = dfu.own_shock_node({'shock_id': file['shock_id'], 'make_handle': 1})
        out_files.append(_get_file_data(shock, file))
    return out_files


def validate_paths(name, files):
    """
    Raise an exception if any `path` value in `files` is non-existent
    """
    for file in files:
        if ('path' in file) and (not os.path.isfile(file['path'])):
            raise ValueError(
                'File path does not exist: ' + file['path']
                + ' . Make sure the file exists in your scratch directory.'
            )


def _get_file_data(shock, file):
    """
    Create a report file dict -- corresponds to the LinkedFile in the KIDL spec
    :param shock: a shock dict with id, handle, etc
    :param file: a dict with shock_id, name, description, label
    :returns: a dict that can be used for the `html_links` or `file_links` in the report
    """
    return {
        'handle': shock['handle']['hid'],
        'description': file.get('description', ''),
        'name': file.get('name', ''),
        'label': file.get('label', ''),
        'URL': shock['handle']['url'] + '/node/' + shock['handle']['id']
    }
