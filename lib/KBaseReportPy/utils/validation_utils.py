from voluptuous import Schema, Required, All, Length, Url

""" Utilities for validating parameters """


def validate_simple_report_params(params):
    """ Validate all parameters to KBaseReportPyImpl#create """
    schema = Schema({
        Required('workspace_name'): All(basestring, Length(min=1)),
        'workspace_id': int,
        Required('report'): {
            'text_message': basestring,
            'warnings': [basestring],
            'objects_created': [ws_object],
            'file_links': [linked_file],
            'html_links': [linked_file],
            'direct_html': basestring,
            'direct_html_link_index': int
        }
    })
    return schema(params)


def validate_extended_report_params(params):
    """ Validate all parameters to KBaseReportPyImpl#create_extended_report """
    schema = Schema({
        Required('workspace_name'): basestring,
        'message': basestring,
        'objects_created': [ws_object],
        'warnings': [basestring],
        'html_links': [linked_file],
        'direct_html': basestring,
        'direct_html_link_index': int,
        'file_links': [linked_file],
        'report_object_name': basestring,
        'html_window_height': float,
        'summary_window_height': float,
        'workspace_id': int
    })
    return schema(params)


# Re-used validations

ws_object = {
    'ref': basestring,
    'description': basestring
}

linked_file = {
    'shock_id': basestring,
    'path': basestring,
    'handle_ref': basestring,
    'description': basestring,
    'name': basestring,
    'label': basestring,
    'URL': Url()
}
