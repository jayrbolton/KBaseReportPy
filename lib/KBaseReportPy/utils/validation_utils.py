from voluptuous import Schema, Required, All, Length, Url

""" Utilities for validating parameters """


def validate_simple_report_params(params):
    """ Validate all parameters to KBaseReportPyImpl#create """
    schema = Schema({
        Required('workspace_name'): All(str, Length(min=1)),
        'workspace_id': int,
        Required('report'): {
            'text_message': str,
            'warnings': [str],
            'objects_created': [ws_object],
            'file_links': [linked_file],
            'html_links': [linked_file],
            'direct_html': str,
            'direct_html_link_index': int
        }
    })
    return schema(params)


def validate_extended_report_params(params):
    """ Validate all parameters to KBaseReportPyImpl#create_extended_report """
    schema = Schema({
        Required('workspace_name'): str,
        'message': str,
        'objects_created': [ws_object],
        'warnings': [str],
        'html_links': [linked_file],
        'direct_html': str,
        'direct_html_link_index': int,
        'file_links': [linked_file],
        'report_object_name': str,
        'html_window_height': float,
        'summary_window_height': float,
        'workspace_id': int,
    })
    return schema(params)


# Re-used types

ws_object = {
    'ref': str,
    'description': str
}

linked_file = {
    'shock_id': str,
    'path': str,
    'handle_ref': str,
    'description': str,
    'name': str,
    'label': str,
    'URL': Url()
}
