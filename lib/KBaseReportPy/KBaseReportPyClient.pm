package KBaseReportPy::KBaseReportPyClient;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

KBaseReportPy::KBaseReportPyClient

=head1 DESCRIPTION


Module for a simple WS data object report type.


=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => KBaseReportPy::KBaseReportPyClient::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my %arg_hash2 = @args;
	if (exists $arg_hash2{"token"}) {
	    $self->{token} = $arg_hash2{"token"};
	} elsif (exists $arg_hash2{"user_id"}) {
	    my $token = Bio::KBase::AuthToken->new(@args);
	    if (!$token->error_message) {
	        $self->{token} = $token->token;
	    }
	}
	
	if (exists $self->{token})
	{
	    $self->{client}->{token} = $self->{token};
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 create

  $info = $obj->create($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a KBaseReportPy.CreateParams
$info is a KBaseReportPy.ReportInfo
CreateParams is a reference to a hash where the following keys are defined:
	report has a value which is a KBaseReportPy.Report
	workspace_name has a value which is a string
	workspace_id has a value which is an int
Report is a reference to a hash where the following keys are defined:
	text_message has a value which is a string
	warnings has a value which is a reference to a list where each element is a string
	objects_created has a value which is a reference to a list where each element is a KBaseReportPy.WorkspaceObject
	file_links has a value which is a reference to a list where each element is a KBaseReportPy.LinkedFile
	html_links has a value which is a reference to a list where each element is a KBaseReportPy.LinkedFile
	direct_html has a value which is a string
	direct_html_link_index has a value which is an int
WorkspaceObject is a reference to a hash where the following keys are defined:
	ref has a value which is a KBaseReportPy.ws_id
	description has a value which is a string
ws_id is a string
LinkedFile is a reference to a hash where the following keys are defined:
	handle has a value which is a KBaseReportPy.handle_ref
	description has a value which is a string
	name has a value which is a string
	label has a value which is a string
	URL has a value which is a string
handle_ref is a string
ReportInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a KBaseReportPy.ws_id
	name has a value which is a string

</pre>

=end html

=begin text

$params is a KBaseReportPy.CreateParams
$info is a KBaseReportPy.ReportInfo
CreateParams is a reference to a hash where the following keys are defined:
	report has a value which is a KBaseReportPy.Report
	workspace_name has a value which is a string
	workspace_id has a value which is an int
Report is a reference to a hash where the following keys are defined:
	text_message has a value which is a string
	warnings has a value which is a reference to a list where each element is a string
	objects_created has a value which is a reference to a list where each element is a KBaseReportPy.WorkspaceObject
	file_links has a value which is a reference to a list where each element is a KBaseReportPy.LinkedFile
	html_links has a value which is a reference to a list where each element is a KBaseReportPy.LinkedFile
	direct_html has a value which is a string
	direct_html_link_index has a value which is an int
WorkspaceObject is a reference to a hash where the following keys are defined:
	ref has a value which is a KBaseReportPy.ws_id
	description has a value which is a string
ws_id is a string
LinkedFile is a reference to a hash where the following keys are defined:
	handle has a value which is a KBaseReportPy.handle_ref
	description has a value which is a string
	name has a value which is a string
	label has a value which is a string
	URL has a value which is a string
handle_ref is a string
ReportInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a KBaseReportPy.ws_id
	name has a value which is a string


=end text

=item Description

Function signature for the create() method -- generate a report for an app run.
create_extended() is the preferred method if you have html_links and
file_links, but this is still provided for backwards compatibility.

=back

=cut

 sub create
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function create (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to create:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'create');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "KBaseReportPy.create",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'create',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method create",
					    status_line => $self->{client}->status_line,
					    method_name => 'create',
				       );
    }
}
 


=head2 create_extended_report

  $info = $obj->create_extended_report($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a KBaseReportPy.CreateExtendedReportParams
$info is a KBaseReportPy.ReportInfo
CreateExtendedReportParams is a reference to a hash where the following keys are defined:
	message has a value which is a string
	objects_created has a value which is a reference to a list where each element is a KBaseReportPy.WorkspaceObject
	warnings has a value which is a reference to a list where each element is a string
	html_links has a value which is a reference to a list where each element is a KBaseReportPy.File
	direct_html has a value which is a string
	direct_html_link_index has a value which is an int
	file_links has a value which is a reference to a list where each element is a KBaseReportPy.File
	report_object_name has a value which is a string
	html_window_height has a value which is a float
	summary_window_height has a value which is a float
	workspace_name has a value which is a string
	workspace_id has a value which is an int
WorkspaceObject is a reference to a hash where the following keys are defined:
	ref has a value which is a KBaseReportPy.ws_id
	description has a value which is a string
ws_id is a string
File is a reference to a hash where the following keys are defined:
	path has a value which is a string
	shock_id has a value which is a string
	name has a value which is a string
	description has a value which is a string
ReportInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a KBaseReportPy.ws_id
	name has a value which is a string

</pre>

=end html

=begin text

$params is a KBaseReportPy.CreateExtendedReportParams
$info is a KBaseReportPy.ReportInfo
CreateExtendedReportParams is a reference to a hash where the following keys are defined:
	message has a value which is a string
	objects_created has a value which is a reference to a list where each element is a KBaseReportPy.WorkspaceObject
	warnings has a value which is a reference to a list where each element is a string
	html_links has a value which is a reference to a list where each element is a KBaseReportPy.File
	direct_html has a value which is a string
	direct_html_link_index has a value which is an int
	file_links has a value which is a reference to a list where each element is a KBaseReportPy.File
	report_object_name has a value which is a string
	html_window_height has a value which is a float
	summary_window_height has a value which is a float
	workspace_name has a value which is a string
	workspace_id has a value which is an int
WorkspaceObject is a reference to a hash where the following keys are defined:
	ref has a value which is a KBaseReportPy.ws_id
	description has a value which is a string
ws_id is a string
File is a reference to a hash where the following keys are defined:
	path has a value which is a string
	shock_id has a value which is a string
	name has a value which is a string
	description has a value which is a string
ReportInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a KBaseReportPy.ws_id
	name has a value which is a string


=end text

=item Description

Create a report for the results of an app run -- handles file and html zipping/uploading
If you are using html_links or file_links, this will be more user-friendly than create()

=back

=cut

 sub create_extended_report
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function create_extended_report (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to create_extended_report:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'create_extended_report');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "KBaseReportPy.create_extended_report",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'create_extended_report',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method create_extended_report",
					    status_line => $self->{client}->status_line,
					    method_name => 'create_extended_report',
				       );
    }
}
 
  
sub status
{
    my($self, @args) = @_;
    if ((my $n = @args) != 0) {
        Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
                                   "Invalid argument count for function status (received $n, expecting 0)");
    }
    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
        method => "KBaseReportPy.status",
        params => \@args,
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
                           code => $result->content->{error}->{code},
                           method_name => 'status',
                           data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
                          );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method status",
                        status_line => $self->{client}->status_line,
                        method_name => 'status',
                       );
    }
}
   

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "KBaseReportPy.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'create_extended_report',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method create_extended_report",
            status_line => $self->{client}->status_line,
            method_name => 'create_extended_report',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for KBaseReportPy::KBaseReportPyClient\n";
    }
    if ($sMajor == 0) {
        warn "KBaseReportPy::KBaseReportPyClient version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 ws_id

=over 4



=item Description

* Workspace ID reference - eg. 'ws/id/ver'
* @id ws


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 handle_ref

=over 4



=item Description

* Reference to a handle ID
* @id handle


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 WorkspaceObject

=over 4



=item Description

* Represents a Workspace object with some brief description text
* that can be associated with the object.
* Required arguments:
*     ws_id ref - workspace ID
* @optional description


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a KBaseReportPy.ws_id
description has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a KBaseReportPy.ws_id
description has a value which is a string


=end text

=back



=head2 LinkedFile

=over 4



=item Description

* Represents a file or html archive that the report should link to
* Used in Report and the create() function
* Required arguments:
*     handle_ref handle - Handle ID
*     string name - Plain-text name of the file (shown to the user)
*     string URL - shock URL and ID (`shock['handle']['url'] + '/node/' + shock['handle']['id']`)
* @optional description label


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
handle has a value which is a KBaseReportPy.handle_ref
description has a value which is a string
name has a value which is a string
label has a value which is a string
URL has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
handle has a value which is a KBaseReportPy.handle_ref
description has a value which is a string
name has a value which is a string
label has a value which is a string
URL has a value which is a string


=end text

=back



=head2 Report

=over 4



=item Description

* A simple Report of a method run in KBase.
* Provides a fixed-width, text-based summary message, a list of warnings,
* and a list of objects created.
* Required arguments:
*     string text_message - Readable plain-text report message
* @optional warnings file_links html_links direct_html direct_html_link_index
* @metadata ws length(warnings) as Warnings
* @metadata ws length(text_message) as Message Length
* @metadata ws length(objects_created) as Objects Created


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
text_message has a value which is a string
warnings has a value which is a reference to a list where each element is a string
objects_created has a value which is a reference to a list where each element is a KBaseReportPy.WorkspaceObject
file_links has a value which is a reference to a list where each element is a KBaseReportPy.LinkedFile
html_links has a value which is a reference to a list where each element is a KBaseReportPy.LinkedFile
direct_html has a value which is a string
direct_html_link_index has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
text_message has a value which is a string
warnings has a value which is a reference to a list where each element is a string
objects_created has a value which is a reference to a list where each element is a KBaseReportPy.WorkspaceObject
file_links has a value which is a reference to a list where each element is a KBaseReportPy.LinkedFile
html_links has a value which is a reference to a list where each element is a KBaseReportPy.LinkedFile
direct_html has a value which is a string
direct_html_link_index has a value which is an int


=end text

=back



=head2 CreateParams

=over 4



=item Description

* Parameters for the create() method
* Pass in *either* workspace_name or workspace_id -- only one is needed
* Required arguments:
*    int workspace_id - needed if workspace_name is blank. Preferred as its immutable.
*    string workspace_name - needed if workspace_id is blank. Note that this may change.
*    Report report


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report has a value which is a KBaseReportPy.Report
workspace_name has a value which is a string
workspace_id has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report has a value which is a KBaseReportPy.Report
workspace_name has a value which is a string
workspace_id has a value which is an int


=end text

=back



=head2 ReportInfo

=over 4



=item Description

* The reference to the saved KBaseReport. This is the return object for
* both create() and create_extended()
* Required arguments:
*    ws_id ref
*    string name


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a KBaseReportPy.ws_id
name has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a KBaseReportPy.ws_id
name has a value which is a string


=end text

=back



=head2 File

=over 4



=item Description

* A file to be linked or uploaded for the report. In extended_report(),
* this will get converted into a lower-level LinkedFile before uploading
* Pass in *either* a shock_id or a path. If a path is given, then the file
* will be uploaded.
* Required arguments:
*     string path - only if shock_id is absent. Can be a file or dir path.
*     string shock_id - only if path is absent.
*     string name - plain-text file name -- shown to the user.
* @optional description


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
path has a value which is a string
shock_id has a value which is a string
name has a value which is a string
description has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
path has a value which is a string
shock_id has a value which is a string
name has a value which is a string
description has a value which is a string


=end text

=back



=head2 CreateExtendedReportParams

=over 4



=item Description

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


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
message has a value which is a string
objects_created has a value which is a reference to a list where each element is a KBaseReportPy.WorkspaceObject
warnings has a value which is a reference to a list where each element is a string
html_links has a value which is a reference to a list where each element is a KBaseReportPy.File
direct_html has a value which is a string
direct_html_link_index has a value which is an int
file_links has a value which is a reference to a list where each element is a KBaseReportPy.File
report_object_name has a value which is a string
html_window_height has a value which is a float
summary_window_height has a value which is a float
workspace_name has a value which is a string
workspace_id has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
message has a value which is a string
objects_created has a value which is a reference to a list where each element is a KBaseReportPy.WorkspaceObject
warnings has a value which is a reference to a list where each element is a string
html_links has a value which is a reference to a list where each element is a KBaseReportPy.File
direct_html has a value which is a string
direct_html_link_index has a value which is an int
file_links has a value which is a reference to a list where each element is a KBaseReportPy.File
report_object_name has a value which is a string
html_window_height has a value which is a float
summary_window_height has a value which is a float
workspace_name has a value which is a string
workspace_id has a value which is an int


=end text

=back



=cut

package KBaseReportPy::KBaseReportPyClient::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
