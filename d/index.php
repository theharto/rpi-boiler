<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

$command = "";

if (isset($_REQUEST['a'])) {
	switch($_REQUEST['a']) {
		case 'start':
			$command = "/home/pi/rpi-boiler/rpi_d.sh start nohup";
			break;
		case 'stop':
			$command = "/home/pi/rpi-boiler/rpi_d.sh stop";
			break;
		case 'ps':
			$command = "ps u -u pi,www-data";
			break;
		case 'psa':
			$command = "ps aux";
			break;
		case 'kill':
			$command = "kill " . $_REQUEST['pid'] . " 2>&1";
			break;
		case 'log':
			$command = "cat /var/www/html/codiad/workspace/rpi-boiler/bb.log";
			break;
		case 'reboot':
			$command = "echo reboot | nc -w 0 localhost 5511";
			break;
		case 'poweroff':
			$command = "echo poweroff | nc -w 0 localhost 5511";
			break;
	}
}

if ($command) {
	echo "Command = " . $command . "\n\n";
	system($command, $ret);
	exit(0);
}

?>

<html>
<head>
	<title>rpi-boiler daemon</title>

<script src="jquery-3.2.1.min.js"></script>
<script>

function command(params) {
	var url = "?" + $.param(params);
	
	$("#return-value").text("loading ...");
	
	$.get(url, function(return_string) {
		//success
		$("#return-value").text(return_string);
	}).fail(function(a, b, c) {
		// fail
		$("#return-value").text("Ajax fail");
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
<h1><a href="/d/">rpi-boiler daemon</a></h1>
<ul>
	<li><button onclick="command({ a:'start' })">Start rpi-boiler</button></li>
	<li><button onclick="command({ a:'stop' })">Stop rpi-boiler</button></li>
	<li><button onclick="command({ a:'ps' })">List own processes </button></li>
	<li><button onclick="command({ a:'psa' })">List all processes</button></li>
	<li><button onclick="command({ a:'kill', pid:$('#pid').val() })">kill pid</button>
		<input onchange="command({ a:'kill', pid:$('#pid').val() })" type="text" id="pid" value=""></li>
	<li><button onclick="command({ a:'log' })">Show log</button></li>
	<li><button onclick="command({ a:'reboot' })">Reboot rpi</button></li>
	<li><button onclick="command({ a:'poweroff' })">Poweroff rpi</button></li>
</ul>

<pre>
	<div id="return-value"></div>
</pre>

</body>
</html>
