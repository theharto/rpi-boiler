<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('error_reporting', E_ALL);
ini_set('display_startup_errors', 1);

$dir = '/home/pi/rpi-boiler';

$commands = [
	'start'		=> ['Start rpi-boiler', "$dir/rpi_d.sh start"],
	'stop'		=> ['Stop rpi-boiler', "$dir/rpi_d.sh stop"],
	'ps'		=> ['List own processes', 'ps u -u pi,www-data'],
	'ps_all'	=> ['List all processes', 'ps aux'],
	'ls'		=> ['ls', "ls -l $dir"],
	'br_1'		=> ['<BR>'],
	'log'		=> ['Show bb.log', "cat $dir/bb.log"],
	'salog'		=> ['Show sa.log', "cat $dir/sa.log"],
	'w_log'		=> ['Wipe bb.log', "echo '' > $dir/bb.log 2>&1; ls -l $dir/*.log"],
	'w_salog'	=> ['Wipe sa.log', "echo '' > $dir/sa.log 2>&1; ls -l $dir/*.log"],
	'fix_log'	=> ['Fix log permissions', "chmod g+w $dir/*.log 2>&1; ls -l $dir/*.log"],
	'br_2'		=> ['<BR>'],
	'settings'  => ['Show settings', "cat $dir/settings.json"],
	'del_sets'	=> ['Delete settings', "rm $dir/settings.json"],
	't_sets'	=> ['Touch settings', "touch $dir/settings.json"],
	'fix_sets'	=> ['Fix settings permission', "chmod g+w $dir/settings.json 2>&1; ls -l $dir/settings.json"],
	'br_3'		=> ['<BR>'],
	'reboot'	=> ['Reboot rpi', 'echo reboot | nc -w 0 localhost 5511'],
	'poweroff'	=> ['Poweroff rpi', 'echo poweroff | nc -w 0 localhost 5511']
];

if (isset($_REQUEST['a'])) {
	$c = $commands[$_REQUEST['a']][1];
	echo "Command = $c\n\n";
	system($c . ' 2>&1');
	exit(0);
}

?>

<html>
<head>
	<title>rpi-boiler utils</title>
	<link href="/static/favicon.ico" rel="shortcut icon">

<script src='jquery-3.2.1.min.js'></script>
<script>
	function command(params) {
		var url = '?' + $.param(params);
		
		$('#return-value').text('loading ...');
		console.log("AJAX call to", url);
		
		$.get(url, function(return_string) {
			//success
			$('#return-value').text(return_string);
		}).fail(function(a, b, c) {
			// fail
			$('#return-value').text('Ajax fail');
		});
	}
</script>

<style>
	button {
		margin:2px;
	}
	#return-value{
		border:1px solid grey;
	}
</style>

</head>
<body>
<h1><a href='/d/'>rpi-boiler utils</a></h1>
<ul>
<?php
	foreach ($commands as $k => $v) {
		if ($v[0] == '<BR>')
			echo "<br>\n";
		else
			echo "\t<li><button onclick='command({ a:\"$k\" })'>$v[0]</button></li>\n";
	}
?>
</ul>

<pre>
	<div id='return-value'></div>
</pre>

</body>
</html>
