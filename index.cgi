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
#
################################################################################################################################################################

my $cgi= new CGI;

my $myuser="it.kevind";
# my character seperator
my $sc="::";

################################################################################################################################################################

my $shortdescription=$cgi->param('ShortDescription'); 
my $date=$cgi->param('Date'); 
my $deadline=$cgi->param('Deadline'); 
my $priority=$cgi->param('Priority');
my $title=$cgi->param('Title');
my $dueby=$cgi->param('DueBy');
my $thingstodo=$cgi->param('ThingsToDo');

################################################################################################################################################################

my ($action, $cgi, $db, $dbh, $dbconn);
my ($maxSessions, $sessionCount, $sessionCode, $ipAddress, $activeUser, $activeUserNum);
my $commonHead="<!DOCTYPE html><html>";

################################################################################################################################################################

my $dbname="toDoList";
my $dbhost="localhost";
my $dbuser="todolist";
my $dbpass="qoukli_90P";

################################################################################################################################################################
my ($saveFile, $saveInfo);

$saveFile="/home/$myuser/public_html/cgi-bin/toDoLister/ListerLog.txt";

################################################################################################################################################################

use constant msg_checkLogin=>101;
use constant msg_viewList=>102;
use constant msg_createNew=>103;
use constant msg_loginFail=>104;
use constant msg_logOut => 105;
use constant msg_signUp => 106;
use constant msg_editThing=>107;
use constant msg_deleteFromList=>108;
use constant msg_saveItem => 109;

use constant salt => 'ko';

################################################################################################################################################################

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

################################################################################################################################################################

sub getSessionCode {
# Expects: 
# Returns: 
# Expects: 
  $sessionCode=$cgi->param('id');
  return $sessionCode;
}

################################################################################################################################################################

sub getAction {
# Expects: 
# Returns: 
  $action=$cgi->param('act'); 
}

################################################################################################################################################################

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

################################################################################################################################################################

sub getUserNum {
  my ($q, $qh);
  my $user=$_[0];
  $q="SELECT UserNum FROM Users WHERE Username='$user';";
  $qh=$dbh->prepare($q);
  $qh->execute();
  my $usercode=$qh->fetchrow();
  return $usercode;
}

################################################################################################################################################################

sub getUserName {
  my ($q, $qh);
  my $session=$_[0];
  $q="SELECT User FROM Sessions WHERE ID=?;";
  $qh=$dbh->prepare($q);
  $qh->execute($session);
  my $userName=$qh->fetchrow();
  return $userName;
}

################################################################################################################################################################

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

################################################################################################################################################################

sub loginOK {
# Expects: 
# Returns: 
  $activeUserNum=getUserNum($activeUser);
  $sessionCode=getNewSession($activeUser);
  return viewList();
}

################################################################################################################################################################

sub loginFail {
# Expects: 
# Returns: 
  my $doing=msg_loginFail;
  my $html=<<loginFail_html;
$commonHead
<body>
<div id="main">
<h1>Error in Login</h1>

Please login:
<form action="" method="post">
<input type="hidden" name="act" value="$doing">
<table>
<tr><td>Username:</td><td><input name="username" type="text"></td></tr>
<tr><td>Password:</td><td><input name="password" type="password"></td></tr>
<tr><td colspan="2"><input type="submit" value="login now"></td></tr>
</table>
</form>
<br>
</div>
</body>
</html>
loginFail_html
  return $html;
}

################################################################################################################################################################

sub logOut {
  my ($q, $qh);
  my $msg_logOut=msg_logOut;
  getSessionCode();
  $q="DELETE FROM Sessions WHERE ID LIKE '$sessionCode';";
  $qh=$dbh->prepare($q);
  my $result=$qh->execute();
  if ($result == 1) {
  

  print "<!DOCTYPE html><html><head><title>Treebeard To-Do-Lister</title>";
  print "<style>";
    
  print "
  #main {
    background-color: #00B060; /*Green color*/
    text-align:center; /*this is the only one which can change where the writing is placed*/
    border-width:5px; /*this sets the width of the blue border outline*/
    border-color:#00ffff; /*setting border colour to Light blue */
    border-style:solid;
	
}
  body {
    background-color:gray; /*Gray color*/
    text-align:center;
    margin-left:auto; /*Horizontally centering to left*/
    margin-right:auto;  /*Horizontally centering to right*/
    width:800px; 
    padding:20px;
    }";
    
  print "</style></head>"; 
  print "<body>";
    
  print "<div id=\"main\">";
  print "<h1>Exiting The Forest</h1>";
  print "You Have Been Logged Out";
  print "<br>";
  print "<br>";
    
  print "<a href=\"http://treebeard.ie/~$myuser/cgi-bin/toDoLister/index.cgi\">Return to Sign In</a>";
    
  print "<br>";
  print "<br>";
    
  print "</div>";
  print "</body></html>";

  }
}

################################################################################################################################################################

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
<body>

<div id="main">
<h3>TreeBeard ToDoLister for user $activeUser</h3>
viewList_html1
  foreach (0..2) {  # REPLACE!
    $html .= getList($_);
  }
  
#$listEntries
  $html.=<<viewList_html2;
  
</div>

<br>
<br>

<div id="main">

<br> 

<div id="links">
  <li><a href="?act=$msg_logOut&amp;id=$sessionCode">Log Out</a></li>
  <li><a href="?act=$msg_createNew&amp;id=$sessionCode">Add a new Task</a></li>
  <li><a href="?act=$msg_deleteFromList&amp;id=$sessionCode">Delete From List</a></li>
  <li><a href="?act=$msg_editThing&amp;id=$sessionCode">Edit List</a></li>
</div>

<br>

</div>

</body>
</html>
viewList_html2
  return $html;
}

################################################################################################################################################################


sub getList {
  my ($q, $qh, $html, @thing, $priority);
  $priority=$_[0];
  print "[$activeUserNum]";
  $q="SELECT * FROM ThingsToDo WHERE UserNum='$activeUserNum' AND Priority='$priority';";
  $qh=$dbh->prepare($q);
  $qh->execute();
  $html="<table>";
  while (@thing=$qh->fetchrow_array()) {
    $html .= "<tr>";
    $html .= "<th><a href=\"";
    $html .= "?act=". msg_editThing;
    $html .= "&amp;thing=$thing[0]";
    $html .= "\">$thing[2]</a></th>";
    $html .= "<td>$thing[3]</td>";
    $html .= "<td>$thing[7]</td></tr>";
  }
  $html .= "</table>";
  return $html;
}

################################################################################################################################################################

sub loginDialog {
# Expects: 
# Returns:
  my $doing=msg_checkLogin;
  my $html=<<loginDialog_html;
$commonHead
<center>
<body>
<div id="main">
<h1>Welcome To TreeBeard Forest</h1>
Please login:<br><i><small>or <a href="?act=">sign up</a></small></i>
<form action="" method="post">
<br>
<input type="hidden" name="act" value="$doing">
<table>
<tr><td>Username:</td><td><input name="username" type="text"></td></tr>
<tr><td>Password:</td><td><input name="password" type="password"></td></tr>
<tr><td colspan="2"><input type="submit" value="login now"></td></tr>
</table>
<br>
</div>
</form>
</body>
</html>
loginDialog_html
  return $html;
}

################################################################################################################################################################

sub tooManySessions {
# Expects: 
# Returns:
  my $doing=msg_checkLogin;
  my $html=<<tooManySessions_html;
$commonHead
<body>
<div id="main"
<h1>Sorry My Fellow Ant</h1>

<p>There are too many sessions, you need to remember to logout</p>
</div>

</body>
</html>
tooManySessions_html
  return $html;
}

################################################################################################################################################################

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
<!DOCTYPE html>
  <html>
  <head>
  <link type="text/css" href="/it.kevind/public_html/cgi-bin/toDoLister/todo.css" rel="stylesheet">
  <title>TreeBeard To-Do-Lister </title>
 <style>
#main {
	 background-color: #00B060; /*Green color*/
	 text-align:center; /*this is the only one which can change where the writing is placed*/
	 border-width:5px; /*this sets the width of the blue bor+der outline*/
	 border-color:#00ffff; /*setting border colour to Light blue */
	 border-style:solid;
	
}
body {
	background-color:gray; /*Gray color*/
	text-align:center;
	margin-left:auto; /*Horizontally centering to left*/
	margin-right:auto;  /*Horizontally centering to right*/
	width:900px; 
	padding:20px;
	
}	
}
#links {
	
	text-align:center; /*this is the only one which can change where the writing is placed*/
	background-color: #00ffff; /*highlights a complete line across the menu bar*/	
      
}
#links li {
	margin:0px 7px;
	display:inline;
	background-color:#00ffff;/*this is the color of the links like the homepage videos products the color is light blue*/
}
</style>
</head>
<body>
  
  <div id="main">  
  
  <br>

  <div id="links"> 
  <ul>
  <li><a href=\"http://treebeard.ie/webmail">Webmail</a></li>
  <li><a href=\"http://treebeard.ie/projectsLister/\">Projects Lister</a>
  <li><a href=\"http://treebeard.ie/">Treebeard</a></li>
  <li><a href=\"http://treebeard.ie/~$myuser/cgi-bin/toDoLister/index.cgi/">To-Do-Lister</a></li>
  <li><a href=\"?act=\$msg_logOut&amp;id=\$sessionCode\">Log Out</a></li>
  <ul>
</div>

  <br>
  
</div>

<br>
<br>

</body>
</html>
commonHead_html
}

################################################################################################################################################################

sub sessionCount {
  my ($q, $qh);
  $q="SELECT COUNT(*) FROM Sessions;";
  $qh=$dbh->prepare($q);
  $qh->execute();
  my $count=$qh->fetchrow();
  return $count;
}  

################################################################################################################################################################

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

################################################################################################################################################################

sub makeSessionCode {
  my $tempCode = new String::Random;
  my $thing = $tempCode->randpattern("cnnn");
  return $thing;
}

################################################################################################################################################################

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

################################################################################################################################################################

sub stampSession {
# timestamp this session to avoid expiry
  my ($q, $qh);
  my $timeStamp=time;
  $q="UPDATE Sessions SET Time=$timeStamp WHERE ID=$sessionCode;";
  $qh=$dbh->prepare($q);
  $qh->execute();
}

################################################################################################################################################################

# this is the second page 
sub createNew {
# Expects: 
# Returns: 
  my $tempVar=msg_saveItem;
  my $sessionID=getSessionCode();
  print <<createNew;
  $commonHead
<head>
<title>Second Page</title>
</head> 
<body>

  <div id="main">  
  
  <a href="toDoListinput.html"></a>

  <form action="index.cgi" method="post">
  <input type="hidden" name="act" value="$tempVar">
  <input type="hidden" name="id" value="$sessionID">
  <table>
  <h1>Treebeard To-Do-Lister</h1>
  </table>
  <tr><td><b>Add a Task To the List:</b></td>
  <td><select name=\"Priority\" placeholder="priority"  maxlength="60" style="width:146px; border:1px solid #999999" /> 
  <option name=\" \"> Priority
  <option value=\"High\">High
  <option value=\"Medium\">Medium
  <option value=\"Small\">Small
  </option></select>
  <br>
  <input id="Title" placeholder="Title" name="Title" type="text" maxlength="60" style="width:146px; border:1px solid #999999" />
  <br>
  <input id="ShortDescription" placeholder="ShortDescription" name="ShortDescription" type="text" maxlength="200" style="width:146px; border:1px solid #999999" />
  <br>
  <input id="Date" placeholder="Date" name="Date" type="text" maxlength="60" style="width:146px; border:1px solid #999999" />
  <br>
  <input id="Dueby" placeholder="Dueby" name="DueBy" type="text" maxlength="60" style="width:146px; border:1px solid #999999" />
  <br>
  <input id="ThingsToDo" placeholder="ThingsToDo" name="ThingsToDo" type="text" maxlength="200" style="width:146px; border:1px solid #999999" />
  
  </td></tr>
  </table>
  <br>
  <tr><td colspan="2"><input type="submit" value="Confirm and Save"></td></tr>
  <br>
  <br> 
  </div>
  </form></body></html>
  
createNew
return
}

################################################################################################################################################################

# opening my database file which is called KDLOG.txt
  open FILE, ">> $saveFile"; 
  # puting all the new enterd information from the input fields into that file
  my $saveInfo= "Title: ".$title."Priority: ".$priority." | ShortDescription: ".$shortdescription." | Date: ".$date." | Deadline: ".$deadline." | DueBy: ".$dueby." | ThingsToDo: ".$thingstodo;
  # puting the information into the file
  print FILE "$saveInfo\n";
  # closing the file
  close FILE;

################################################################################################################################################################

# this lets you edit the todolister
sub editList {
# Expects: 
# Returns: 
  my $msg_editThing=msg_editThing;

  print <<editList;
  $commonHead
    <head>
    <title></title>
    </head>
    <body>
    <h3>The Editor</h3>
    
    
    
    </body>
  
editList
}

################################################################################################################################################################

sub deleteFromList {
# Expects: 
# Returns: 
  my $msg_deleteFromList=msg_editList;
 # print <<deleteFromList;
#  $commonHead
 
 
#deleteFromList 
}

################################################################################################################################################################

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
    editList();
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

################################################################################################################################################################

sub printHashPass {
  my ($pass)="pass";
  $pass=crypt $pass, salt;
  print "[$pass]\n";
}

################################################################################################################################################################

# for saving things into the treebeard sql database
sub saveNewItem {
  my ($q, $qh);
  #my $userNum = getUserNum();
  # this puts the inputed information into the SQL TreeBeard database
  $q="INSERT INTO ThingsToDo (ShortDescription, UserNum) VALUES (?, ?);";
  $qh=$dbh->prepare($q);
 # print "[",getSessionCode(),"]";
 # print "[$q]";
  my $userName=getUserName(getSessionCode());
 # print "[$userName]";
  my $userNum=getUserNum($userName);
 # print "[$userNum]";
 # $qh->execute($priority, $userNum);
 # $qh->execute($title, $userNum);
  $qh->execute($shortdescription, $userNum);
  #$qh->execute($date, $userNum);
 # $qh->execute($dueby, $userNum);
 # $qh->execute($thingstodo, $userNum);
  $activeUser=$userName;
  $activeUserNum=$userNum;
  print viewList();
}

################################################################################################################################################################




