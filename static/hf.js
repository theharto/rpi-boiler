const set_cookie = (name, value, days = 7, path = '/') => {
	const expires = new Date(Date.now() + days * 864e5).toUTCString();
	document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=' + path;
}

const get_cookie = (name) => {
	return document.cookie.split('; ').reduce((r, v) => {
    	const parts = v.split('=');
    	return parts[0] === name ? decodeURIComponent(parts[1]) : r;
	}, '');
}

const del_cookie = (name, path) => {
	setCookie(name, '', -1, path);
}

var g_debug_mode = null;

function debug_mode(val = null) {
	if (val === null) {
		if (g_debug_mode === null) {
			g_debug_mode = (get_cookie('hf-debug_mode') == 'true');
		}
		return g_debug_mode;
	}
	g_debug_mode = Boolean(val);
	set_cookie('hf-debug_mode', String(g_debug_mode));
}

function debug() {
	var t = "";
	
	if (!debug_mode())
		return;

	$("#debug").css("display", "block");

	for (var i = 0; i < arguments.length; i++) {
		if (typeof arguments[i] == 'object')
			t += JSON.stringify(arguments[i], null, 4);
		else
			t += arguments[i];
	}
	$("<div class='debug-text'></div>").text(t).prependTo('#debug');
	console.log(t);
}

function urlBase64ToUint8Array(base64String) {
	const padding = '='.repeat((4 - base64String.length % 4) % 4);
	const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
	const rawData = window.atob(base64);
	return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}
