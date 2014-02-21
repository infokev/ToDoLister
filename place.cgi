#!/usr/bin/perl
use strict;
use CGI::Carp ("fatalsToBrowser");
#use treebeard;
#
# PROG:		place-holder index.cgi
# OBJECT:
# AUTHOR:       FAROE
# DATE:         10/2013
#
# VERS a0.0
# 
# Print standardised header

print "Content-Type: text/html\n\n";
topBit(1,2);
print "<meta HTTP-EQUIV=\"refresh\" CONTENT=\"60;URL=http://treebeard.fachtnaroe.net/\">";
bottomBit(3);
topBit(3);
print "treeBeard.fachtnaroe.net<hr>";
print "<b>This is a place-holder file.";
bottomBit(2,1);

sub topBit {
# Expects:
# Returns: 
  my ($last, $expects, @t);
  @t=@_;
  while ($expects=shift @t) {
	$last=$expects;
	  if ($expects==1) {
		if ($expects==$t[0]) {
			&bottomBit($t[0]);
			shift @t;
		}
		print "<html>";
	  }
	  elsif ($expects==2) {
		if ($expects==$t[0]) {
			&bottomBit($t[0]);
			shift @t;
		}
		print "<head>";
	  }
	  elsif ($expects==3) {
		if ($expects) {
			&bottomBit($t[0]);
			shift @t;
		}
		print "<body>";
	  }
  }
}

sub bottomBit {
# Expects:
# Returns: 
  while(my $expects=shift @_) {
	  if ($expects==1) {
		print "</html>\n";
	  }
	  elsif ($expects==2) {
		print "</body>";
	  }
	  elsif ($expects==3) {
		print "</head>";
	  }
  }
}
