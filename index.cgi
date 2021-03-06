#!/usr/bin/perl
use strict;
require "todo_lib.pl";
use CGI;
use DBI;
use String::Random;
#use Crypt::SaltedHash;
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

SignUp
=cut

my $cgi= new CGI;
my $myuser="it.kevind";
# my character seperator
my $sc="::";

my $shortdescription=$cgi->param('ShortDescription'); 
my $date=$cgi->param('Date'); 
my $priority=$cgi->param('Priority');
my $title=$cgi->param('Title');
my $dueby=$cgi->param('DueBy');
my $thingstodo=$cgi->param('ThingsToDo');



my ($action, $cgi, $db, $dbh, $dbconn);
my ($maxSessions, $sessionCount, $sessionCode, $ipAddress, $activeUser, $activeUserNum);
my $commonHead="<!DOCTYPE html><html>";



my $dbname="toDoList";
my $dbhost="localhost";
my $dbuser="todolist";
my $dbpass="qoukli_90P";


my ($saveFile, $saveInfo);

$saveFile="/home/$myuser/public_html/cgi-bin/toDoLister/ListerLog.txt";

use constant msg_checkLogin=>101;
use constant msg_viewList=>102;
use constant msg_createNew=>103;
use constant msg_loginFail=>104;
use constant msg_logOut => 105;
use constant msg_signUp => 106;
use constant msg_editThing=>107;
use constant msg_deleteFromList=>108;
use constant msg_saveItem => 109;
use constant msg_saveEdit => 110;

use constant salt => 'ko';

# this is the first page
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
  $commonHead=<<commonHead_html
  
<!DOCTYPE html><html>
<head>
<title>TreeBeard ToDo Lister</title>
<link rel="stylesheet" type="text/css" href="todo.css">
</head>
  
  <div id="main"><br>
 
  <img src="todolist.jpg" width="450" height="100" alt="todolist.jpg">
 
  <div id="links"> 
  
  <ul>
  <li><a href="http://treebeard.ie/webmail">Webmail</a></li>
  <li><a href="http://treebeard.ie/projectsLister">Projects Lister</a>
  <li><a href="http://treebeard.ie">Treebeard</a></li>
  <li><a href="http://treebeard.fachtnaroe.net/~$myuser/cgi-bin/toDoLister/index.cgi">ToDo List</a></li>
  </ul>
  
</div><br></div><br><br>

commonHead_html
}

# this is the second page 
sub createNew {
# Expects: 
# Returns: 
  my $tempVar=msg_saveItem;
  my $sessionID=getSessionCode();
  print <<createNew;
  $commonHead

  <div class="main">  
  
  <a href="toDoListinput.html"></a>

  <form action="index.cgi" method="post">
  <input type="hidden" name="act" value="$tempVar">
  <input type="hidden" name="id" value="$sessionID">
  <br>
  <br>
  <table>
  <tr><td><b>Add a Task To the List:</b></td>
  
  <td><select name="Priority" style="width:146px; border:1px solid #999999" > 
  <option value="0">High </option>
  <option value="5">Medium </option>
  <option value="10">Lowest
  </option></select>
  
  <input id="Title" placeholder="Title" name="Title" type="text" maxlength="60" style="width:146px; border:1px solid #999999" >
  <input id="ShortDescription" placeholder="ShortDescription" name="ShortDescription" type="text" maxlength="200" style="width:146px; border:1px solid #999999" >
  
  <input id="Date" placeholder="Date YYYY/MM/DD" name="Date" type="text" maxlength="60" style="width:146px; border:1px solid #999999" >
  <input id="Dueby" placeholder="Dueby YYYY/MM/DD" name="DueBy" type="text" maxlength="60" style="width:146px; border:1px solid #999999" >
  <input id="ThingsToDo" placeholder="ThingsToDo" name="ThingsToDo" type="text" maxlength="200" style="width:146px; border:1px solid #999999" >
  </td></tr></table>
 

  <input type="submit" value="Confirm and Save">
  <br><br><br>
  </form>
  </div>
 
createNew
return
}

# this lets you edit the todolister
sub editThing {
# Expects: 
# Returns: 
  my $msg_editThing=msg_editThing;
  my $thing=getRecordNumber();
  my ($thingKey, $user, $title, $desc, $priority, $date, $due, $detail)=getRecord($thing);
  my ($high, $med, $low);
  
  if ($priority==0) {
    $high="<option value=\"0\" selected >High</option>";
  }
  else {
    $high="<option value=\"0\">High</option>";
  }
 
  if (($priority != 0) && ($priority != 10) ) {
    $med="<option value=\"5\" selected >Medium</option>";
  }
  else {
    $med="<option value=\"5\">Medium</option>";
  }
  if ($priority==10) {
    $low="<option value=\"10\" selected >Low</option>";
  }
  else {
    $low="<option value=\"10\">Low</option>";
  }
  my $doing=msg_saveEdit;
  print <<editThing;
  $commonHead
 
  <div class="main">
  <h3>The Editor</h3>
  <p>Make Your Changes Here</p> 
  <form action=" " method="post">
  <br>
  <input type="hidden" name="act" value="$doing">
  <input type="hidden" name="thing" value="$thing">
  <select name="Priority" style="width:146px; border:1px solid #999999" > 
  $high$med$low
  </select>
  <input id="Title" name="Title" value="$title" type="text" maxlength="60" style="width:146px; border:1px solid #999999" >
  <input id="ShortDescription" value="$desc" name="ShortDescription" type="text" maxlength="200" style="width:146px; border:1px solid #999999" >
  <input id="Date" name="Date" value="$date" type="text" maxlength="60" style="width:146px; border:1px solid #999999" >
  <input id="Dueby" name="DueBy" value="$due" type="text" maxlength="60" style="width:146px; border:1px solid #999999" >
  <input id="ThingsToDo" name="ThingsToDo" value="$detail" type="text" maxlength="200" style="width:146px; border:1px solid #999999" >
  <br>
  <br>
  <input type="submit" value="Save Changes">
  </form>
  <br><br>
  </div>


editThing

}

sub saveEdit {
  my $recordNum=getRecordNumber();
  my ($priority)=$cgi->param('Priority');
  my ($title)=$cgi->param('Title');
  my ($desc)=$cgi->param('ShortDescription');
  my ($date)=$cgi->param('Date');
  my ($due)=$cgi->param('DueBy');
  my ($detail)=$cgi->param('ThingsToDo');
  my ($q, $qh);
  $q="UPDATE ThingsToDo SET Priority=?, ShortDescription=?, Title=?, Date=?, DueBy=?, ThingToDo=? WHERE thingKey=?;";
  $qh = $dbh->prepare($q);
  my $result= $qh->execute($priority, $desc, $title, $date, $due, $detail, $recordNum);

}

sub newConnection {
# Expects: 
# Returns: 
  if (sessionCount() < $maxSessions) {
    print loginDialog();
  }
  else {
  # too many sessions
  print "[".sessionCount()."][$maxSessions]";
    print tooManySessions();
  }
}

sub getSessionCode {
# Expects: 
# Returns: 
# Expects: 
  $sessionCode=$cgi->param('id');
  return $sessionCode;
}

sub getAction {
# Expects: 
# Returns: 
  $action=$cgi->param('act'); 
}

sub getRecordNumber {
# Expects: 
# Returns: 
  my $thing=$cgi->param('thing'); 
  return $thing;
}

sub getRecord {
  my $recordNum=shift;
  my ($q, $qh, @record);
  $q="SELECT * FROM ThingsToDo WHERE thingKey=?;";
  $qh = $dbh->prepare($q);
  $qh->execute($recordNum);
  @record = $qh->fetchrow_array();
  return @record;
}

sub passwordOK {
  my $user=$_[0];
  my $pass=$_[1];
  my ($q, $qh, $count);
  $pass=crypt $pass, salt;
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

sub getUserNum {
  my ($q, $qh);
  my $user=$_[0];
  $q="SELECT UserNum FROM Users WHERE Username='$user';";
  $qh=$dbh->prepare($q);
  $qh->execute();
  my $usercode=$qh->fetchrow();
  return $usercode;
}

sub getUserName {
  my ($q, $qh);
  my $session=$_[0];
  $q="SELECT User FROM Sessions WHERE ID=?;";
  $qh=$dbh->prepare($q);
  $qh->execute($session);
  my $userName=$qh->fetchrow();
  return $userName;
}

sub checkLogin {
# Expects: 
# Returns: 
  my $user=$cgi->param('username');
  my $pass=$cgi->param('password');
  if (passwordOK($user, $pass)) {
    $activeUser=$user;
    print loginOK();
  }
  else {
    print loginFail();
  }
}

sub loginOK {
# Expects: 
# Returns: 
  $activeUserNum=getUserNum($activeUser);
  $sessionCode=getNewSession($activeUser);
  return viewList();
}

sub loginFail {
# Expects: 
# Returns: 
  my $doing=msg_loginFail;
  my $html=<<loginFail_html;
$commonHead
<body>
<div class="main">
<h1>Error in Login</h1>

Please login:
<form action="" method="post">
<input type="hidden" name="act" value="$doing">

<table>
<tr><td>Username:</td><td><input name="username" type="text"></td></tr>
<tr><td>Password:</td><td><input name="password" type="password"></td></tr>
<tr><td colspan="2"><input type="submit" value="login now"></td></tr>
</table>
</form><br>
</div></body></html>

loginFail_html
  return $html;
}

sub logOut {
  my ($q, $qh);
  my $msg_logOut=msg_logOut;
  getSessionCode();
  $q="DELETE FROM Sessions WHERE ID LIKE '$sessionCode';";
  $qh=$dbh->prepare($q);
  my $result=$qh->execute();
  if ($result == 1) {
  
  print "<!DOCTYPE html><html><head><title>Treebeard ToDo List</title>";
  print "<link rel=\"stylesheet\" type=\"text/css\" href=\"todo.css\">";
  print "</head>"; 
  print "<body>";
  
  print "<div id=\"main\"><br>
 
  <img src=\"todolist.jpg\" width=\"450px\" height=\"100px\">
 
  <div id=\"links\"> 
  
  <ul>
  <li><a href=\"http://treebeard.ie/webmail\">Webmail</a></li>
  <li><a href=\"http://treebeard.ie/projectsLister/\">Projects Lister</a>
  <li><a href=\"http://treebeard.ie/\">Treebeard</a></li>
  <li><a href=\"http://treebeard.fachtnaroe.net/~$myuser/cgi-bin/toDoLister/index.cgi\">ToDo List</a></li>
  </ul>
  
  </div><br></div><br><br>";
    
  print "<div id=\"main\">";
  print "<h1>Exiting The Forest</h1>";
  print "You Have Been Logged Out";
  print "<br><br>";
  print "<a href=\" http://treebeard.fachtnaroe.net/~it.kevind/cgi-bin/toDoLister/index.cgi\">Return to Sign In</a><br><br>";
  #print "<a href=\"http://treebeard.ie/~$myuser/cgi-bin/toDoLister/index.cgi\">Return to Sign In</a><br><br>";
    
  print "</div></body></html>";
  }
}

sub viewList {
# Expects: 
# Returns: 
  my $doing=msg_viewList;
  my $msg_logOut=msg_logOut;
  my $msg_createNew=msg_createNew;
  my $msg_editThing=msg_editThing;
  my $msg_deleteFromList=msg_deleteFromList;
  my $listEntries;#=getList(); #$activeUser, $sessionCode);
  my $html=<<viewList_html1;
  
$commonHead

<div class="main">

<h3>TreeBeard ToDo List for user $activeUser</h3>
<input type="submit" value="Delete Selected">
viewList_html1
# this is for the drop down priority it lets a priority number passed in shows up
  foreach (0..10) {  # REPLACE!
    $html .= getList($_);
  }
  
#$listEntries
  $html.=<<viewList_html2;
  
</div><br><br>

<div class="main"><br>

<div class="links">
  <li><a href="?act=$msg_logOut&amp;id=$sessionCode">Log Out</a></li>
  <li><a href="?act=$msg_createNew&amp;id=$sessionCode">Add a new Task</a></li>
</div><br>

</div>

</body></html>
viewList_html2
  return $html;
}

sub loginDialog {
# Expects: 
# Returns:
  my $doing=msg_checkLogin;
  my $html=<<loginDialog_html;
$commonHead

<div class="main">

<h1>Welcome To TreeBeard Forest</h1>

Please login:<br><i><small>or <a href="?act=">sign up</a></small></i>
<form action=" " method="post">
<br>
<input type="hidden" name="act" value="$doing">

<table>
<tr><td>Username:</td><td><input name="username" type="text"></td></tr>
<tr><td>Password:</td><td><input name="password" type="password"></td></tr>
<tr><td colspan="2"><input type="submit" value="Login Now"></td></tr>
</table>
<br>

</form>
</div>
</body></html>

loginDialog_html
  return $html;
}

sub tooManySessions {
# Expects: 
# Returns:
  my $doing=msg_checkLogin;
  my $html=<<tooManySessions_html;
$commonHead
<body>
<div class="main"
<h1>Sorry My Fellow Ant</h1>

<p>There are too many sessions, you need to remember to logout</p>
</div>

</body></html>
tooManySessions_html
  return $html;
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
  }
}

sub makeSessionCode {
  my $tempCode = new String::Random;
  my $thing = $tempCode->randpattern("cnnn");
  return $thing;
}

sub checkSession {
# does this session id exist
  my ($q, $qh);
  my $code=$_[0];
  $q="SELECT COUNT(*) FROM Sessions WHERE ID LIKE '$code';";
  $qh=$dbh->prepare($q);
  $qh->execute();
  my $count=$qh->fetchrow();
  if ($count != 1) {
    print "Non-existent session";
    exit;
  }
}

sub stampSession {
# timestamp this session to avoid expiry
  my ($q, $qh);
  my $timeStamp=time;
  $q="UPDATE Sessions SET Time=$timeStamp WHERE ID=$sessionCode;";
  $qh=$dbh->prepare($q);
  $qh->execute();
}

sub deleteFromList {
# Expects: 
# Returns: 
  my $msg_deleteFromList=msg_editThing;
 # print <<deleteFromList;
#  $commonHead
 
#deleteFromList 
}

sub printHashPass {
  my ($pass)="pass";
  $pass=crypt $pass, salt;
  print "[$pass]\n";
}

# this gets information from the ThingsToDo folder in the SQL database
sub getList {
  my ($q, $qh, $html, @thing, $priority);
  # any priority number passed in so its not restricted to 1 priority number
  $priority=shift;
  # this is for experimental purposes
  # print "[$activeUserNum]";
  # selects Title shortdescription date dueby thingtodo from the SQL database
  $q="SELECT * FROM ThingsToDo WHERE UserNum='$activeUserNum' AND Priority='$priority';";
  $qh=$dbh->prepare($q);
  $qh->execute();
  $html="<table width=\"100%\">";
  while (@thing=$qh->fetchrow_array()) {
    $html .= "<tr>";
    $html .= "<th><a href=\"";
    $html .= "?act=". msg_editThing;
    $html .= "&amp;thing=$thing[0]";
    $html .= "\">$thing[2]</a></th>";
    $html .= "<td>$thing[3]</td>";
    $html .= "<td>$thing[4]</td>";
    $html .= "<td>$thing[5]</td>";
    $html .= "<td>$thing[6]</td>";
    $html .= "<td>$thing[7]</td>";
    $html .= "<td><input type=\"checkbox\" name=\"delete\" value=\"delete\"></td></tr>";
    
  }
  $html .= "</table>";
 
  return $html;
}

# for saving things into the ThingsToDo Folder in the treebeard sql database
sub saveNewItem {
  my ($q, $qh);
  # my $userNum = getUserNum();
  # This querys the information in the SQL database folder ThingsToDo
  $q="INSERT INTO ThingsToDo (UserNum, Title, ShortDescription, Priority, Date, DueBy, ThingToDo) VALUES (?, ?, ?, ?, ?, ?, ?);";
  $qh=$dbh->prepare($q);
  # print "[",getSessionCode(),"]";
  # print "[$q]";
  my $userName=getUserName(getSessionCode());
  # print "[$userName]";
  my $userNum=getUserNum($userName);
  # print "[$userNum]";
  # gets the values
  $qh->execute($userNum, $title, $shortdescription, $priority, $date, $dueby, $thingstodo);
  $activeUser=$userName;
  $activeUserNum=$userNum;
  # prints the values in the ThingsToDo database
  print viewList();
}

# opening my personal database file which is called ListerLog.txt
  open FILE, ">> $saveFile"; 
  # puting all the new enterd information from the input fields into that file
  my $saveInfo= "Title: ".$title."Priority: ".$priority." | ShortDescription: ".$shortdescription." | Date: ".$date." | DueBy: ".$dueby." | ThingsToDo: ".$thingstodo;
  # puts the information into the file
  print FILE "$saveInfo\n";
  # closing the file
  close FILE;

# variables

sub main {
  initVars();
  contentType();
#saveNewItem();
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
    createNew();
  }
  elsif ($action == msg_editThing) {
    editThing();
  }
  elsif ($action == msg_saveEdit) {
    saveEdit();
  }  
  elsif ($action == msg_deleteFromList) {
    msg_deleteFromList();
  }
  elsif ($action == msg_logOut) {
    logOut();
  }
  elsif ($action == msg_saveItem) {
    saveNewItem();
  }
  else {
    newConnection();
  }
}
main();
