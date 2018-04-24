/*
    Module for a simple WS data object report type.
*/
module KBaseReportPy {
    /*
     * Workspace ID reference - eg. 'ws/id/ver'
     * @id ws
     */
    typedef string ws_id;

    /*
     * Reference to a handle ID
     * @id handle
     */
    typedef string handle_ref;

    /*
     * Represents a Workspace object with some brief description text
     * that can be associated with the object.
     * Required arguments:
     *     ws_id ref - workspace ID
     * @optional description
     */
    typedef structure {
        ws_id ref;
        string description;
    } WorkspaceObject;

    /*
     * Represents a file or html archive that the report should link to
     * Used in Report and the create() function
     * Required arguments:
     *     handle_ref handle - Handle ID
     *     string name - Plain-text name of the file (shown to the user)
     *     string URL - shock URL and ID (`shock['handle']['url'] + '/node/' + shock['handle']['id']`)
     * @optional description label
     */
    typedef structure {
        handle_ref handle;
        string description;
        string name;
        string label;
        string URL;
    } LinkedFile;

    /*
     * A simple Report of a method run in KBase.
     * Provides a fixed-width, text-based summary message, a list of warnings,
     * and a list of objects created.
     * Required arguments:
     *     string text_message - Readable plain-text report message
     * @optional warnings file_links html_links direct_html direct_html_link_index
     * @metadata ws length(warnings) as Warnings
     * @metadata ws length(text_message) as Message Length
     * @metadata ws length(objects_created) as Objects Created
     */
    typedef structure {
        string text_message;
        list<string> warnings;
        list<WorkspaceObject> objects_created;
        list<LinkedFile> file_links;
        list<LinkedFile> html_links;
        string direct_html;
        int direct_html_link_index;
    } Report;

    /*
     * Parameters for the create() method
     * Pass in *either* workspace_name or workspace_id -- only one is needed
     * Required arguments:
     *    int workspace_id - needed if workspace_name is blank. Preferred as its immutable.
     *    string workspace_name - needed if workspace_id is blank. Note that this may change.
     *    Report report
     */
    typedef structure {
        Report report;
        string workspace_name;
        int workspace_id;
    } CreateParams;

    /*
     * The reference to the saved KBaseReport. This is the return object for
     * both create() and create_extended()
     * Required arguments:
     *    ws_id ref
     *    string name
     */
    typedef structure {
        ws_id ref;
        string name;
    } ReportInfo;

    /*
     * Function signature for the create() method -- generate a report for an app run.
     * create_extended() is the preferred method if you have html_links and
     * file_links, but this is still provided for backwards compatibility.
     */
    funcdef create(CreateParams params)
        returns (ReportInfo info) authentication required;

    /*
     * A file to be linked or uploaded for the report. In extended_report(),
     * this will get converted into a lower-level LinkedFile before uploading
     * Pass in *either* a shock_id or a path. If a path is given, then the file
     * will be uploaded.
     * Required arguments:
     *     string path - only if shock_id is absent. Can be a file or dir path.
     *     string shock_id - only if path is absent.
     *     string name - plain-text file name -- shown to the user.
     * @optional description
     */
    typedef structure {
        string path;
        string shock_id;
        string name;
        string description;
    } File;

    /*
     * Parameters used to create a more complex report with file and html links
     *
     * All parameters are optional.
     *
     * string message - Simple text message to store in report object
     * list<WorkspaceObject> objects_created - List of result workspace objects that this app
     *     has created. They will get linked in the report view.
     * list<string> warnings - A list of plain-text warning messages
     * list<File> html_links - A list of paths or shock IDs pointing to html files or directories.
     *     if you pass in paths, they will be zipped and uploaded
     * int direct_html_link_index - Index in html_links to set the direct/default view in the
     *     report (ignored if direct_html is present).
     * string direct_html - simple html text that will be rendered within the report widget
     *     (do not use both this and html_links -- use one or the other)
     * list<File> file_links - a list of file paths or shock node IDs. Allows the user to
     *     specify files that the report widget should link for download.
     * string report_object_name - name to use for the report object
     *     (will be auto-generated if unspecified)
     * html_window_height - fixed height in pixels of the html window for the report
     * summary_window_height - fixed height in pixels of the summary window for the report
     * string workspace_name - name of workspace where object should be saved
     * int workspace_id - id of workspace where object should be saved
     *
     * @metadata ws length(warnings) as Warnings
     * @metadata ws length(text_message) as Message Length
     * @metadata ws length(objects_created) as Objects Created
     * @metadata ws length(html_links) as HTML Links
     * @metadata ws length(file_links) as File Links
     * @optional message objects_created warnings html_links direct_html direct_html_link_index file_links report_object_name html_window_height summary_window_height
     */
    typedef structure {
        string message;
        list<WorkspaceObject> objects_created;
        list<string> warnings;
        list<File> html_links;
        string direct_html;
        int  direct_html_link_index;
        list<File> file_links;
        string report_object_name;
        float html_window_height;
        float summary_window_height;
        string workspace_name;
        int workspace_id;
    } CreateExtendedReportParams;

    /*
     * Create a report for the results of an app run -- handles file and html zipping/uploading
     * If you are using html_links or file_links, this will be more user-friendly than create()
     */
    funcdef create_extended_report(CreateExtendedReportParams params)
        returns (ReportInfo info) authentication required;
};
