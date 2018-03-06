<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('error_reporting', E_ALL);
ini_set('display_startup_errors', 1);

$dir = '/home/pi/rpi-boiler';
define('AUTH_FILENAME', $dir . '/utils_auth.json');
define('AUTH_COOKIE_NAME', 'hf-utils-key');
define('AUTH_DEFAULT_PW', 'default');
define('AUTH_COOKIE_TTL', 86400); // 24h

#
#	load_auth()
#
function load_auth() {
	if (!file_exists(AUTH_FILENAME)) {
		$a = [ "pw" => AUTH_DEFAULT_PW, "sessions" => [] ];
		save_auth($a);
		return $a;
	}
	if (!$a = json_decode(file_get_contents(AUTH_FILENAME), true))
		die("Auth file json corrupted - " . AUTH_FILENAME);
	
	# remove expired sessions
	$t = time();
	foreach ($a['sessions'] as $session_key => $session_expiry) {
		if ($t > $session_expiry) {
			unset($a['sessions'][$session_key]);
			#echo "removed expired session $session_key";
		}
	}
	#echo "loaded: ";
	#print_r($a);
	return $a;
}

#
#	save_auth()
#
function save_auth($a) {
	if (!file_put_contents(AUTH_FILENAME, json_encode($a)))
		die("Failed to write to auth file - " . AUTH_FILENAME);
	#echo "saved: ";
	#print_r($a);
}


#
#	START
#

$authenticated = false;
$auth = load_auth();

#
#	if logging in, create session
#
if (isset($_REQUEST['pw']) && $_REQUEST['pw'] == $auth['pw']) {
	$key = bin2hex(random_bytes(16));
	#echo "password match " . $key;
	$auth["sessions"][$key] = time() + AUTH_COOKIE_TTL;
	setcookie(AUTH_COOKIE_NAME, $key);
	$authenticated = true;
	save_auth($auth);
}

#
#	check cookie is valid session key
#
if (isset($_COOKIE[AUTH_COOKIE_NAME]) && isset($auth['sessions'][$_COOKIE[AUTH_COOKIE_NAME]])) {
	$authenticated = true;
}

if (!$authenticated) { 
	?>
		<html><head>
			<title>Homefire Utils</title>
			<link href="/static/favicon.ico" rel="shortcut icon">
		</head><body>
		<form method="post">
			<input type="password" name="pw" placeholder="Password" autofocus>
		</form>
		</body></html>
	<?php
	exit(1);
}

$commands = [
	'start'		=> ['Start rpi-boiler', "$dir/rpi_d.sh start null_out"],
	'stop'		=> ['Stop rpi-boiler', "$dir/rpi_d.sh stop"],
	'ps'		=> ['List own processes (p)', 'ps u -u pi,www-data'],
	'ps_all'	=> ['List all processes', 'ps aux'],
	'ls'		=> ['ls (l)', "ls -l $dir; ls -l $dir/logs"],
	'br_1'		=> ['<BR>'],
	'log'		=> ['Show bb.log (b)', "cat $dir/logs/bb.log"],
	'salog'		=> ['Show sa.log (a)', "cat $dir/logs/sa.log"],
	'butlog'	=> ['Show but.log', "cat $dir/logs/but.log"],
	'w_log'		=> ['Wipe bb.log', "echo '' > $dir/logs/bb.log 2>&1; ls -l $dir/logs", 1],
	'w_salog'	=> ['Wipe sa.log', "echo '' > $dir/logs/sa.log 2>&1; ls -l $dir/logs", 1],
	'w_butlog'	=> ['Wipe but.log', "echo '' > $dir/logs/but.log 2>&1; ls -l $dir/logs", 1],
	'fix_log'	=> ['Fix log permissions', "chmod g+w $dir/logs/*.log 2>&1; ls -l $dir/logs/*.log"],
	'br_2'		=> ['<BR>'],
	'settings'  => ['Show settings (s)', "cat $dir/settings.json"],
	'del_sets'	=> ['Delete settings', "rm $dir/settings.json", 1],
	't_sets'	=> ['Touch settings', "touch $dir/settings.json"],
	'fix_sets'	=> ['Fix settings permission', "chmod g+w $dir/settings.json 2>&1; ls -l $dir/settings.json"],
	'br_3'		=> ['<BR>'],
	'reboot'	=> ['Reboot rpi', 'echo reboot | nc -w 0 localhost 5511', 1],
	'poweroff'	=> ['Poweroff rpi', 'echo poweroff | nc -w 0 localhost 5511', 1],
	'br_4'		=> ['<BR>'],
	'ls_v_l'	=> ['ls /var/log', "ls -l /var/log"],
	'del_v_l'	=> ['delete /var/log', "echo rm_var_logs | nc -w 0 localhost 5511", 1]
];

if (isset($_REQUEST['a'])) {
	$c = $commands[$_REQUEST['a']][1];
	echo "Command = $c\n\n";
	system($c . ' 2>&1');
	exit(1);
}

?>

<html>
<head>
	<title>Homefire Utils</title>
	<link href="/static/favicon.ico" rel="shortcut icon">

<script src='jquery-3.2.1.min.js'></script>
<script>
	function command(c, conf) {
		
		if (conf && !confirm('Do [' + c + ']?'))
			return;
		
		var url = '?a=' + c;
		
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
	
	$(document).keypress(function(e) {
		switch(e.key) {
			<?php
				foreach ($commands as $k => $v) {
					$l = strlen($v[0]);
					if ($v[0][$l - 1] == ')') {
						$c = $v[0][$l - 2];
						echo "case '$c':\n";
						echo "\tcommand('$k', 0);\n";
						echo "\tbreak;\n";
					}
				}
			?>
			case 'r':
				location.reload();
				break;
		}
	});
	
</script>

<style>
	body {
		font: 12pt sans-serif;
	}
	button {
		margin: 2px;
	}
	#return-value {
		border: 1px solid grey;
	}
	.pw_warning {
		width: 30%;
		color: red;
		margin: auto;
		padding: 10px;
		text-align: center;
		border: 1px solid red;
	}
</style>

</head>
<body>

<?php
if ($auth['pw'] == AUTH_DEFAULT_PW)
	echo "<div class='pw_warning'>Change default password!</div>\n";
?>

<h1><a href='/utils/'>Homefire Utils</a></h1>
<a href="/">Back</a>
<ul>
<?php
	foreach ($commands as $k => $v) {
		if ($v[0] == '<BR>')
			echo "<br>\n";
		else {
			if (!isset($v[2]))
				$v[2] = 0;
			echo "\t<li><button onclick='command(\"$k\", $v[2])'>$v[0]</button></li>\n";
		}
	}
?>
</ul>
<pre>
	<div id='return-value'></div>
</pre>
</body>
</html>
