#!/usr/bin/perl
use strict;
require "todo_lib.pl";
use CGI;
use DBI;
use String::Random;
use CGI::Carp ("fatalsToBrowser");

=begin
Possibilities: 
Connect
LoginOK
LoginFail
ViewList
Add to list
Delete from list
Logout
=cut

my ($action, $cgi, $db, $dbh, $dbconn);
my ($maxSessions, $sessionCount, $sessionCode, $ipAddress, $activeUser);

my $dbname="toDoList";
my $dbhost="localhost";
my $dbuser="todolist";
my $dbpass="qoukli_90P";

use constant msg_checkLogin=>101;
use constant msg_viewList=>102;
use constant msg_createNew=>103;
use constant msg_loginFail=>104;

sub newConnection {
# Expects: 
# Returns: 
  if (sessionCount() < $maxSessions) {
    print loginDialog();
  }
  else {
  # too many sessions
    print tooManySessions();
  }
}

sub getSessionCode {
# Expects: 
# Returns: 
# Expects: 
  $sessionCode=$cgi->param('id');
}

sub getAction {
# Expects: 
# Returns: 
  $action=$cgi->param('act'); 
}

sub passwordOK {
  my $user=$_[0];
  my $pass=$_[1];
  my ($q, $qh, $count);
  $q="SELECT COUNT(*) FROM Users WHERE Username='$user' AND Password='$pass';";
  $qh = $dbh->prepare($q);
  $qh->execute();
  $count = $qh->fetchrow();
  if ($count == 1) {
    return 1;
  }
  else {
    return 0;
  }
}

sub checkLogin {
# Expects: 
# Returns: 
  my $user=$cgi->param('username');
  my $pass=$cgi->param('password');
  if (passwordOK($user, $pass)) {
    $activeUser=$user;
    $sessionCode=getNewSession($activeUser);
    print viewList();
  }
  else {
    print loginFail();
  }
}

sub loginOK {
# Expects: 
# Returns: 

}

sub loginFail {
# Expects: 
# Returns: 
  my $doing=msg_loginFail;
  my $html=<<loginFail_html;
<!DOCTYPE html>
<html>
<head>
</head>
<body>
<h1>Error</h1>

Please login:
<form action="" method="post">
<input type="hidden" name="act" value="$doing">
<table>
<tr><td>Username:</td><td><input name="username" type="text"></td></tr>
<tr><td>Password:</td><td><input name="password" type="password"></td></tr>
<tr><td colspan="2"><input type="submit" value="login now"></td></tr>
</table>
</form>
</body>
</html>
loginFail_html
  return $html;

}

sub viewList {
# Expects: 
# Returns: 
  my $doing=msg_viewList;
  my $html=<<viewList_html;
<!DOCTYPE html>
<html>
<head>
</head>
<body>
<h1>To Do List for $activeUser</h1>
<p>...</p>
</body>
</html>
viewList_html
  return $html;
}

sub createNew {
# Expects: 
# Returns: 

}

sub addToList {
# Expects: 
# Returns: 

}

sub deleteFromList {
# Expects: 
# Returns: 

}

sub logout {
# Expects: 
# Returns: 

}

sub loginDialog {
# Expects: 
# Returns:
  my $doing=msg_checkLogin;
  my $html=<<loginDialog_html;
<!DOCTYPE html>
<html>
<head>
</head>
<body>
<h1>Welcome</h1>
Please login:
<form action="" method="post">
<input type="hidden" name="act" value="$doing">
<table>
<tr><td>Username:</td><td><input name="username" type="text"></td></tr>
<tr><td>Password:</td><td><input name="password" type="password"></td></tr>
<tr><td colspan="2"><input type="submit" value="login now"></td></tr>
</table>
</form>
</body>
</html>
loginDialog_html
  return $html;
}

sub tooManySessions {
# Expects: 
# Returns:
  my $doing=msg_checkLogin;
  my $html=<<tooManySessions_html;
<!DOCTYPE html>
<html>
<head>
</head>
<body>
<h1>Sorry</h1>
<p>Too many sessions</p>
</body>
</html>
tooManySessions_html
  return $html;
}

sub initVars {
  my ($q, $qh);
  $cgi=new CGI;
  $dbconn="dbi:mysql:$dbname;$dbhost";
  $dbh = DBI->connect($dbconn, $dbuser, $dbpass);
  $q="SELECT Value FROM Variables WHERE NAME='MaxSessions';";
  $qh=$dbh->prepare($q);
  $qh->execute();
  $maxSessions=$qh->fetchrow();
  # what about $ENV{REMOTE_HOST}print $q;
  $ipAddress =  $ENV{REMOTE_ADDR};
}

sub sessionCount {
  my ($q, $qh);
  $q="SELECT COUNT(*) FROM Sessions;";
  $qh=$dbh->prepare($q);
  $qh->execute();
  my $count=$qh->fetchrow();
  return $count;
}  

sub getNewSession {
# this is a new session, get an ID if possible
  my ($q, $qh);
  my $user=$_[0];
  if (sessionCount() < $maxSessions) {
    #
    my $session=makeSessionCode();
    $q="INSERT INTO Sessions (ID, Time, IPv4, User) VALUES (?, ?, ?, ?);";
    $qh=$dbh->prepare($q);
    $qh->execute($session, time, $ipAddress, $user);
    return $session;
    
  }
  else {
    #
  }
}

sub makeSessionCode {
  my $tempCode = new String::Random;
  my $thing = $tempCode->randpattern("cnnn");
  return $thing;
}

sub checkSession {
# does this session id exist
}

sub stampSession {
# timestamp this session to avoid expiry
  my ($q, $qh);
  my $timeStamp=time;
  $q="UPDATE Sessions SET Time=$timeStamp WHERE ID=$sessionCode;";
  $qh=$dbh->prepare($q);
  $qh->execute();
}

sub main {
  initVars();
  contentType();

  getAction();
  if ($action == msg_checkLogin) {
    checkLogin();
  }
  elsif ($action == msg_loginFail) {
    checkLogin();
  }
  elsif ($action == msg_viewList) {
    viewList();
  }
  elsif ($action == msg_createNew) {
  
  }
  else {
    newConnection();
  }

}

main();