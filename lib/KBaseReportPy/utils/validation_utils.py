# -*- coding: utf-8 -*-
from voluptuous import Schema, Required, All, Length, Url

"""
Utilities for validating parameters
We use the `voluptuous` schema validation library
More info here: https://pypi.org/project/voluptuous/
"""


def validate_simple_report_params(params):
    """ Validate all parameters to KBaseReportPyImpl#create """
    schema = Schema({
        'workspace_name': non_empty_string,
        'workspace_id': int,
        Required('report'): {
            'text_message': basestring,
            'warnings': [basestring],
            'objects_created': [ws_object],
            'direct_html': basestring,
        }
    })
    return __require_workspace(schema(params))


def validate_extended_report_params(params):
    """ Validate all parameters to KBaseReportPyImpl#create_extended_report """
    schema = Schema({
        'workspace_name': non_empty_string,
        'workspace_id': int,
        'message': basestring,
        'objects_created': [ws_object],
        'warnings': [basestring],
        'html_links': [extended_file],
        'direct_html': basestring,
        'direct_html_link_index': int,
        'file_links': [extended_file],
        'report_object_name': basestring,
        'html_window_height': float,
        'summary_window_height': float
    })
    return __require_workspace(schema(params))


def __require_workspace(params):
    """
    We need either workspace_id or workspace_name, but we don't need both
    voluptuous doesn't have good syntax for that, so we do it manually
    """
    if ('workspace_id' not in params) and ('workspace_name' not in params):
        raise ValueError(
            'Invalid params: either `workspace_name` or `workspace_id` is required: '
            + str(params)
        )
    return params


# Re-used validations

non_empty_string = All(basestring, Length(min=1))

# Workspace object (corresponding to the KIDL spec's WorkspaceObject)
ws_object = {
    Required('ref'): non_empty_string,
    'description': basestring
}

# Type validation for .create's LinkedFile (see KIDL spec)
linked_file = {
    'handle': basestring,
    'description': basestring,
    'name': basestring,
    'label': basestring,
    'URL': Url()
}

# Type validation for the extended report's File (see KIDL spec)
extended_file = {
    'name': non_empty_string,
    'shock_id': basestring,
    'path': basestring,
    'description': basestring
}
