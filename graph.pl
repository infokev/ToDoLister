#!/usr/bin/perl
use strict;
use GD;
use DBI;
use Date::Parse;
use MIME::Base64;
use CGI::Carp ("fatalsToBrowser");
use CGI;

my ($graph, $white, $black, $red, $blue, $green, $orange);
my ($width, $height, $step) = (400, 200, 5);
$graph = new GD::Image($width, $height);
$white = $graph->colorAllocate(255,255,255); # 0
$black = $graph->colorAllocate(0,0,0);   #1
$red = $graph->colorAllocate(255,0,0);  #2
$blue = $graph->colorAllocate(0,0,255);#3
$green = $graph->colorAllocate(0,255,0);#4
$orange = $graph->colorAllocate(91, 71, 0); #5
print "Content-type: text/html\n\n";
print "<html><head></head><body>\n";
my $cgi= new CGI;
my $parms=$cgi->param('mod');
$graph->setThickness(2);
#Y axis:
$graph->line($step*2+2, $height-$step*2, $step*2+2, 0+$step, $black);
#X axis:
$graph->line($step*2, $height-$step*2, $width-$step, $height-$step*2, $black);

$graph->string(gdSmallFont, $step*2+2, $height-$step*2-2, "time--->", $black);
$graph->stringUp(gdSmallFont, 0, $height-$step*2, "time_since_last_activity--->", $black);

my $dbname="Students2013";
my $dbhost="localhost";
my $dbuser="todolist";
my $dbpass="qoukli_90P";

my ($q, $qh, @data, %items, $code, $start, $end, $x, $y, $when, $last, $tsl);
my ($db, $dbh, $dbconn);

$dbconn="dbi:mysql:$dbname;$dbhost";
$dbh = DBI->connect($dbconn, $dbuser, $dbpass);
$graph->setThickness(1);
$q="SELECT PPS, TimeStamp FROM ResultsLog;";
$qh=$dbh->prepare($q);
$qh->execute();

# start is    2013-06-27 21:26:23
# end is    2013-08-26 09:00:00
$start=str2time('2013-06-26 21:00:00');
$end=str2time('2013-07-01 00:00:00');
$end=$end-$start;
$last=0;
$tsl=0;

my %items=('Connect', $green, 'login', $green, 'login_FAIL', $red, 'ViewResult', $blue, 'C2N_conn', $orange, 'C2N_name', $orange);
$y=$height;
while (@data=$qh->fetchrow_array()) {
  $code=999;
  for my $test(keys %items) {
    if ($data[0] =~ m/$test/) {
      $code=$items{$test};
    }
  }

  #if ($code != 999) {
    $when=str2time($data[1])-$start;
    #print "[$start] [$when] [$end]\n";
    $tsl=$when-$last;
    $last=$when;
    if (($when >= 0) && ($when <= $end)) {
      $x=int (($when/$end)*$width)+ ($step);
      #$x=int (str2time($data[1])-me($start))/($end-$start);
      $y=($height-$tsl-$step*2)-2;
      if ($y < 0) {
        $y = 1;
      }
     # print "($x, $y)\n";
     #print "$code\n";
     if ($code == 999) {
       $code=$red;
     }
     if ($code==$blue) {
       $graph->filledRectangle($x-1,$y-1,$x+1,$y+1,$blue);
     }
     else {
       $graph->setPixel($x, $y, $code);
     }
    }
  #}
}
#for my $grid(
my $a=int (((str2time('2013-06-27 21:26:33')-$start)/$end)*$width)+3;#
print "<h1>Online results viewing</h1><h2>Graph of activity <i>vs</i> time</h2>";
$graph->line($a, 0, $a,$height, $red);
$graph->stringUp(gdTinyFont, $a-10, $height/4+$step*2-2, "27/6 21:26", $red);
str2time('2013-06-27 09:00:00');
$a=int (((str2time('2013-06-28 09:00:00')-$start)/$end)*$width)+3;#
$graph->line($a, 0, $a,$height, $red);
$graph->stringUp(gdTinyFont, $a-10, $height/4+$step*2-2, "28/6 09:00", $red);
str2time('2013-06-27 12:00:00');
$a=int (((str2time('2013-06-28 12:00:00')-$start)/$end)*$width)+3;#
$graph->line($a, 0, $a,$height, $red);
$graph->stringUp(gdTinyFont, $a-10, $height/4+$step*2-2, "28/6 12:00", $red);
$a=int (((str2time('2013-06-28 17:00:00')-$start)/$end)*$width)+3;#
$graph->line($a, 0, $a,$height, $red);
$graph->stringUp(gdTinyFont, $a-10, $height/4+$step*2-2, "28/6 17:00", $red);
$a=int (((str2time('2013-06-30 0:00:00')-$start)/$end)*$width)+3;#
$graph->line($a, 0, $a,$height, $red);
$graph->stringUp(gdTinyFont, $a-10, $height/4+$step*2-2, "30/6 00:00", $red);
$a=int (((str2time('2013-06-27 23:59:00')-$start)/$end)*$width)+3;#
$graph->line($a, 0, $a,$height, $red);
$graph->stringUp(gdTinyFont, $a-10, $height/4+$step*2-2, "27/6 23:59", $red);

$graph->filledRectangle(310,18,315,23,$blue);
$graph->string(gdTinyFont, 320, 15, "=Results Viewed", $blue);

open FILE, "> image.png";
binmode(FILE);
print FILE $graph->png;
my $image=encode_base64($graph->png);
close FILE;
$width*=2;
$height*=2;
$image= "<img width=\"$width\" height=\"$height\" src=\"data:image/png;base64,$image\">";
print $image;
print "\n</body></html>\n";