<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

$command = "";

if (isset($_REQUEST['a'])) {
	switch($_REQUEST['a']) {
		case 'start':
			$command = "/var/www/html/codiad/workspace/rpi-boiler/rpi_d.sh start nohup";
			break;
		case 'stop':
			$command = "/var/www/html/codiad/workspace/rpi-boiler/rpi_d.sh stop";
			break;
		case 'ps':
			$command = "ps u -u pi,www-data";
			break;
		case 'psa':
			$command = "ps aux";
			break;
		case 'kill':
			$command = "kill " . $_REQUEST['pid'];
			break;
		case 'log':
			$command = "cat /var/www/html/codiad/workspace/rpi-boiler/bb.log";
	}
}


?>


<html>
<head>
	<title>rpi-boiler daemon</title>

<script>
function kill_process() {
	command({ a:"kill", pid:document.getElementById("pid").value });
}

function command(params) {
	var form = document.createElement("form");
	form.setAttribute("method", "get");

	for (var key in params) {
		var input = document.createElement("input");
		input.setAttribute("name", key);
		input.setAttribute("value", params[key]);
		input.setAttribute("type", "hidden");
		form.appendChild(input);
	}
	document.body.appendChild(form);
	form.submit();
}

</script>

</head>

<body>
<h1>rpi-boiler daemon</h1>
<ul>
	<li><button onclick="command({ a:'start' })">Start rpi-boiler</button></li>
	<li><button onclick="command({ a:'stop' })">Stop rpi-boiler</button></li>
	<li><button onclick="command({ a:'ps' })">List own processes </button></li>
	<li><button onclick="command({ a: 'psa' })">List all processes</button></li>
	<li>
		<button onclick="kill_process()">kill pid</button>
		<input onchange="kill_process()" type="text" id="pid" value="">
	</li>
	<li><button onclick="command({ a:'log' })">Show log</button></li>
</ul>

<pre>
<?php
if ($command) {
	echo "Command = " . $command . "\n\n";
	system($command . " 2>&1", $ret);
}
?>
</pre>

</body>
</html>
