
# KBaseReportPy

This is a [KBase SDK](https://github.com/kbase/kb_sdk) app that can be used within other apps to generate output reports in the narrative.

[How to create a KBaseReport](https://github.com/kbase/kb_sdk/blob/master/doc/howto/create_a_report.md)

# API

Install in your own KBase SDK app with:

```sh
$ kb-sdk install KBaseReportPy
```

## Initialization

Initialize the client using the `callback_url` from your `MyModuleImpl.py` class:

```py
from KBaseReportPy.KBaseReportPyClient import KBaseReportPy
...
report_client = KBaseReportPy(self.callback_url)
```

## Creating a report

To create a report, use the following parameters:

* `message`: (optional string) basic result message to show in the report
* `report_object_name`: (optional string) a name to give the workspace object that stores the report (will use job ID if unspecified)
* `workspace_id`: (optional integer) id of your workspace. Preferred over `workspace_name` as it's immutable. Required if `workspace_name` is absent.
* `workspace_name`: (required string) string name of your workspace. Requried if `workspace_id` is absent.
* `direct_html`: (optional string) raw HTML to show in the report
* `objects_created`: (optional list of WorkspaceObject) data objects that were created as a result of running your app, such as assemblies or genomes
* `warnings`: (optional list of strings) any warnings messages generated from running the app
* `file_links`: (optional list of dicts) files to attach to the report (see the valid key/vals below)
* `html_links`: (optional list of dicts) HTML files to attach and display in the report (see the additional information below)
* `direct_html_link_index`: (optional integer) index in `html_links` that you want to use as the main/default report view
* `html_window_height`: (optional float) fixed pixel height of your report view
* `summary_window_height`: (optional float) fixed pixel height of the summary within your report

Use the method **`report_client.create_extended_report(params)`** to create a report object:

```py
report = report_client.create_extended_report({
    'direct_html_link_index': 0,
    'html_links': [html_file],
    'report_object_name': report_name,
    'workspace_name': workspace_name
})
```

### File links and HTML links

The `file_links` and `html_links` params can have the following keys:

* `shock_id`: (required string) Shock ID for a file. Not required if `path` is present.
* `path`: (required string) Full file path for a file (in scratch). Not required if `shock_id` is present.
* `name`: (required string) name of the file
* `description`: (optional string) Readable description of the file

For `html_links`, you can pass in the path for a directory that contains website data and an `index.html` file. KBaseReport will automatically zip up the directory for you and upload it to the workspace. If you set the `html_links` index of that HTML directory in `direct_html_link_index`, then the report widget will render your full html directory in an iframe.

Any additional images or linked files that live in your HTML directory will be accessible from your `index.html` and can be linked to and rendered in your report widget.

> Important: Be sure to set the name of your main HTML file (eg. `index.html`) to the `'name'` key in your `html_links`.

For example, to use an HTML directory:

```
html_dir = {
    'path': html_dir_path,
    'name': 'index.html',  # MUST match the filename of the main html
    'description': 'My HTML report'
}
report = report_client.create_extended_report({
    'html_links': [html_dir],
    'direct_html_link_index': 0,
    'report_object_name': report_name,
    'workspace_name': workspace_name
})
```
