
function reduce0(f) {
	return function() { f(); }
}

function reduce(f, a) { 
	return function() { return f(a); };
}

function reduce11(f, a) { 
	return function(e) { return f(e, a); };
}

function reduce2(f, a1, a2) { 
	return function() { return f(a1, a2); };
}

function reduce3(f, a1, a2, a3) { 
	return function() { return f(a1, a2, a3); };
}

function extend(ctor, obj) {
	obj.constructor = ctor;
	ctor.call(obj);
}

function show(obj) {
	var s = obj.toString() + "\n";
	for (p in obj)
		s += p + ": " + obj[p] + "\n";
	alert(s);
}

function block(el, t, to) {
	var e = el != undefined ? $(el)[0] : document;
	e.uiBlocked = true;

	var a = {
		message: '<img width="64px" height="64px" ' + 
				'src="/static/loading.gif">',
		css: {
			backgroundColor: 'inherit',
	 		color: 'inherit',
	 		border: 'none'
		},
		fadeIn: t
	};
	
	var f = function() {
		if (!e.uiBlocked) 
			return;
		if (el != undefined)
			$(el).block(a);
		else
			$.blockUI(a);
	};

	if (to != undefined)
		e.uiBlockTimeout = setTimeout(f, to);
	else
		f();
}

function unblockElement(el, t, onUnblock) {
	var e =	$(el)[0];
	e.uiBlocked = false;
	clearTimeout(e.uiBlockTimeout);

	if (t != undefined)
		$(el).unblock({ fadeOut: t, onUnblock: onUnblock });
	else
		$(el).unblock({ onUnblock: onUnblock });
}

function unblock(t, onUnblock) {
	document.uiBlocked = false;
	clearTimeout(document.uiBlockTimeout);

	if (t != undefined)
		$.unblockUI( { fadeOut: t, onUnblock: onUnblock });
	else
		$.unblockUI( { onUnblock: onUnblock });
}

function json(method, url, obj, success, error, complete) {
	return $.ajax({
		url: url,
		type: method,
		cache: false,
		dataType: 'json',
		data: obj,
		async: true,
		success: success,
		error: error,
		complete: complete
	});
}

function jsonGet(url, obj, success, error, complete) {
	return json('GET', url, obj, success, error, complete);
}

function jsonPut(url, obj, success, error, complete) {
	return json('PUT', url, obj, success, error, complete);
}


