<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('error_reporting', E_ALL);
//ini_set('display_startup_errors', 1);

define('DIR', '/home/pi/rpi-boiler/');

$commands = [
	'start'		=> ['Start rpi-boiler', DIR . 'rpi_d.sh start'],
	'stop'		=> ['Stop rpi-boiler', DIR . 'rpi_d.sh stop'],
	'ps'		=> ['List own processes', 'ps u -u pi,www-data'],
	'ps_all'	=> ['List all processes', 'ps aux'],
	'log'		=> ['Show log', 'cat ' . DIR . 'bb.log'],
	'elog'		=> ['Show error log', 'cat ' . DIR . 'bb_err.log'],
	'del_logs'	=> ['Wipe logs', 'echo "" > ' . DIR . 'bb.log 2>&1; echo "" > ' . DIR . 'bb_err.log 2>&1; ls -l ' . DIR . '*.log'],
	'fix_log'	=> ['Fix log permissions', 'chmod g+w ' . DIR . '*.log 2>&1; ls -l ' . DIR . '*.log'],
	'reboot'	=> ['Reboot rpi', 'echo reboot | nc -w 0 localhost 5511'],
	'poweroff'	=> ['Poweroff rpi', 'echo poweroff | nc -w 0 localhost 5511'],
	'ls'		=> ['ls', 'ls -l ' . DIR],
	'settings'  => ['Show settings', 'cat ' . DIR . 'settings.json'],
	'del_settings'	=> ['Delete settings', 'rm ' . DIR . 'settings.json'],
	'fix_settings'	=> ['Fix settings permission', 'chmod g+w ' . DIR . 'settings.json 2>&1; ls -l ' . DIR . 'settings.json']
];

if (isset($_REQUEST['a'])) {
	$c = $commands[$_REQUEST['a']][1];
	echo "Command = $c\n";
	system($c . ' 2>&1');
	exit(0);
}

?>

<html>
<head>
	<title>rpi-boiler utils</title>

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
		echo "\t<li><button onclick='command({ a:\"$k\" })'>$v[0]</button></li>\n";
	}
?>
</ul>

<pre>
	<div id='return-value'></div>
</pre>

</body>
</html>
