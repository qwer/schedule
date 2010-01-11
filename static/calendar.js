function DateTime(date, time) {
	if (arguments.length == 2) {
		this.date = date;
		this.times = time;
	}
	this.toString = function() {
		return "" + date + "  " + this.times.start + "-" + this.times.end;
	}
}

function Date(year, month, day) {
	if (arguments.length == 3) {
		this.year = year;
		this.month = month;
		this.dat = day;
	}
	this.toString = function() {
		return this.year + "-" + this.month + "-" + this.day;
	};
	this.compare = function(d) {
		return d.year == this.year && d.month == this.month && d.day == this.day; 
	}
}

function Time(hours, minutes) {
	if (arguments.length == 2) {
		this.hours = hours;
		this.minutes = minutes;
	}
	this.toString = function() {
		return (this.hours < 10 ? "0" : "") + this.hours + ":" +
			(this.minutes < 10 ? "0" : "") + this.minutes; 
	};
	this.compare = function(t) {
		return t.hours == this.hours && t.minutes == this.minutes; 
	}
}

function createCalendar(id) {
	var div = $('#' + id)[0];
	var cells = div.cells = [];
	
	var table = document.createElement('table');
	table.setAttribute('id', id + '_table');
	table.setAttribute('class', 'calendar');
	table.setAttribute('cellpadding', '0px');
	table.setAttribute('cellspacing', '1px');
	div.appendChild(table);

	days = days.split(' ');
	var row = document.createElement('tr');
	row.setAttribute('id', id + '_header');
	row.setAttribute('class', 'calendar_hdr');
	table.appendChild(row);
	for (var j = 0; j < 8; j++)  {
		var cell = document.createElement('th');
		cell.setAttribute('id', id + '_hdr_' + j);
		if (j > 0)
			cell.innerHTML = days[j - 1] + ' ' + 
					dates[j - 1].day + '.' + dates[j - 1].month;
		cell.onclick = reduce(cellClick, cell);
		row.setAttribute('class', 'calendar_th');
		row.appendChild(cell);
	}
	
	for (var i = 0; i < times.length; i++) {
		var row = document.createElement('tr');
		row.setAttribute('id', id + '_row_' + i);
		row.setAttribute('class', 'calendar_tr');
		table.appendChild(row);
		var cc = [];
		cells[i] = cc; 
		for (var j = 0; j < 8; j++)  {
			var td = document.createElement('td');
			td.setAttribute('width', '12%');
			var cell = td; //document.createElement('div');
			//cell.setAttribute('width', '100%');
			//cell.setAttribute('height', '100%');
			cell.setAttribute('class', 'event');
			//td.appendChild(cell);
			cell.setAttribute('id', id + '_cell_' + i + '_' + j);
			//cell.innerHTML = 'cell ' + i + ', '  + j;
			if (j == 0)
				cell.innerHTML = times[i].start + "-" + times[i].end;
			else
				cc[j - 1] = cell; 
			cell.time = times[i];
			cell.xindex = j - 1;
			cell.yindex = i; 
			cell.onclick = reduce(cellClick, cell);
			cell.onmousedown = reduce11(cellMouseDown, cell);
			td.onclick = reduce(cellClick, cell);
			cell.data = null;
			td.setAttribute('class', 'calendar_td');
			row.appendChild(td);
		}
	}
	if (events)
		for (var i = 0; i < events.length; i++) {
			createEvent2(events[i]);
		}
}

function EventData() {
	this.name = null;
	this.where = null;
	this.when = null;
	this.who = null;
}


function cellClick(cell)
{
	var e = $('#event-name')[0];
	cellSelect(cell);
	form.cell = cell;
	form.eventWhen.innerHTML = getCellDateTime(cell);//cell.time.start + "-" + cell.time.end;
	if (cell.data) {
		$("option", form.eventWhere).each(function(i) {
			this.selected = this.innerHTML == cell.data.where;
		});
		form.eventName.value = cell.data.name;
		$('#no').attr("value", "Delete");
		$('#yes').attr("value", "Save");
	} else {
		form.eventName.value = 'Новое мероприятие';
		$("option", form.eventWhere).each(function(i) { this.selected = false; });
		$('#no').attr("value", "Cancel");
		$('#yes').attr("value", "Create");
	}
	showForm();
}

function showForm() {
	$.blockUI({
		message: $('#question'),
		css: {
			border:'1px solid', padding: '0em', 
			background: 'inherit',
			width: '100%', height:'100%', 
			position: 'fixed', top: '0px', left:'0px'
		},
		overlayCSS: { background: 'inherit', cursor: 'arrow'},
		fadeIn: 0, fadeOut: 0
	});
	
	//$('.message')[0].onclick = function(e) { return false; } ;
	//document.getElementById('question').onclick = noClick;
	$('.blockOverlay').click(noClick);
}

var d = { x: 0, y: 0 };
var dragging = false;
var dragElement = null;
var background = null;
var dropCell = null;

function getPos2(el) {
	var left = 0;
	var top = 0;
	//if (el.offsetParent) {
		do {
			left += el.offsetLeft;
			top += el.offsetTop;
		} while (el = el.offsetParent);
	//}
	return { x: left, y: top };
}

function getPos(el) {
	if (el.getBoundingClientRect) {
		var box = el.getBoundingClientRect();
		var body = document.body;
		var docElem = document.documentElement;
		var scrollTop = window.pageYOffset || docElem.scrollTop || body.scrollTop;
		var scrollLeft = window.pageXOffset || docElem.scrollLeft || body.scrollLeft;
		var clientTop = docElem.clientTop || body.clientTop || 0;
		var clientLeft = docElem.clientLeft || body.clientLeft || 0;
		var top  = box.top +  scrollTop - clientTop;
		var left = box.left + scrollLeft - clientLeft;
		return { x: Math.round(left), y: Math.round(top) };
	} else
		return getPos2(el); 
}

function createBackground() {
	background = $('<div></div>');
	background.appendTo($('body')[0]);
	background.css('left', 0);
	background.css('top', 0);
	background.width('100%');
	background.height('100%');
	background.css('position', 'fixed');
	background.css('z-index',  9998);
}

function showBackground() {
	background.css('display', 'block');
}

function hideBackground() {
	background.css('display', 'none');
}

function cellMouseDown(e, cell) {
	if (!cell.data)
		return;
	//alert('mouse down ' + cell.innerHTML)
	dragging = true;
	dragElement = cell;
	
	if (!e)
		e = window.event;
	var mousePos = mouseCoords(e);

	var pos = getPos(cell);
	//alert(mousePos.x + ', ' + mousePos.y);
	d.x = pos.x - mousePos.x;
	d.y = pos.y - mousePos.y;
	$('#d').html(d.x + ' ' + d.y + '<br/>' + pos.x + ' ' + pos.y);
	return false;
}

function createCopy() {
	var a = $('<div>' + dragElement.innerHTML + '</div>');
	var pos = getPos(dragElement);
	a.appendTo($('body')[0]);
	$(a).css('position', 'absolute');
	$(a).css('left', pos.x);
	$(a).css('top',  pos.y);
	$(a).css('z-index', 9999);
	$(a).css('background', '#fff');
	$(a).css('width',  $(dragElement).width());
	$(a).css('height', $(dragElement).height());
	$(a).css('border', 'solid 1px');
	$(a).attr('class', 'calendar_td calendar-data');
	dragElement.copy = a;
}

function findCell(p) {
	var el = null;
	$('#calendar_table').children().children('td').each(function (i) {
		var pos = getPos(this);
		pos.x -= d.x;
		pos.y -= d.y;
		var w = this.offsetWidth;
		var h = this.offsetHeight;
		if (Math.abs(p.x - pos.x) < w / 4 &&
			Math.abs(p.y - pos.y) < h / 4) {  
		//if (p.x >= pos.x && p.x < pos.x + w && //$(this).width() &&
		//	p.y >= pos.y && p.y < pos.y + h) {//$(this).height()) {
			//alert(this.innerHTML);
				$('#cell').html(this.innerHTML + '    ' + p.x + ', ' + p.y + 
					'   ' + $(this).width() + ':' + $(this).height());
				el = this;
		}
	});
	return el;
}

function showCopy() {
	dragElement.copy.css('display', 'block');
}

function hideCopy() {
	dragElement.copy.css('display', 'none');
}

function mouseDown(e) {
	return;
	if (!e)
		e = window.event;
	
	var pos = mouseCoords(e);
	box.css('left', bx = pos.x);
	box.css('top', by = pos.y);
}
var bx, by;
function mouseDrag(e) {
	return;
	if (!e)
		e = window.event;
	var mousePos = mouseCoords(e);
	box.css('width', mousePos.x - bx);
	box.css('height', mousePos.y - by);
}

function mouseMove(e) {
	if (!e)
		e = window.event;
	
	$('#drag').html(' ' + e.clientX + ', ' + e.clientY);
	if (!dragging) 
		return;

	if (!background)
		createBackground();
	showBackground();
	
	if (!dragElement.copy) {
		createCopy();
		dragElement.innerHTML = '';
	}

	var mousePos = mouseCoords(e);
	//alert(mousePos.x + ', ' + mousePos.y);
	var el = dragElement.copy;
	$(el).css('left', mousePos.x + d.x);
	$(el).css('top',  mousePos.y + d.y);

	var cell = findCell(mousePos);
	if (cell) {
		if (dropCell != cell) {
			if (cell.data == null) {
				if (dropCell)
					dropCell.innerHTML = '';
				cell.innerHTML = el.html();
				dropCell = cell;
				hideCopy();
			} else {
				if (dropCell)
					dropCell.innerHTML = dragElement.innerHTML;
				dragElement.innerHTML = cell.innerHTML;
				cell.innerHTML = el.html();
				hideCopy();
				dropCell = cell;
			}
		}
	} else {
		showCopy();
		if (dropCell)
			dropCell.innerHTML = dragElement.innerHTML;
		dragElement.innerHTML = '';
		dropCell = null;
		$('#cell').html('null');
	}
}

function mouseUp(e) {
	if (!dragging)
		return;
	if (!e)
		e = window.event;
	dragging = false;
	if (background)
		hideBackground();
	var mousePos = mouseCoords(e);
	var cell = findCell(mousePos);
	if (cell) {
		moveEvent(dragElement, cell);
	} else {
		if (dragElement.copy)
			dragElement.innerHTML = dragElement.copy.html(); 
	}
	if (dragElement.copy) {
		dragElement.copy.remove();
		dragElement.copy = null;
	}
	dragElement = null;
	dropCell = null;
}

function mouseCoords(ev) { 
	if (ev.pageX || ev.pageY)
		return { x:ev.pageX, y:ev.pageY };  
	return { 
		x:ev.clientX + document.body.scrollLeft - document.body.clientLeft, 
		y:ev.clientY + document.body.scrollTop  - document.body.clientTop 
	}; 
}

function cellSelect(cell)
{
	$(cell).attr('class', 'calendar_td calendar-selected');
}

function cellDeselect(cell)
{
	$(cell).attr('class', cell.data ? 'calendar_td calendar-data' : 'calendar_td');
}

function moveEvent(cell1, cell2) {
	var data1 = cell1.data;
	var data2 = cell2.data;
	if (data2)
		setCellData(cell1, data2.name, data2.where, data2.when, data2.who);
	else
		setCellData(cell1, null);
	if (data1)
		setCellData(cell2, data1.name, data1.where, data1.when, data1.who);
	else
		setCellData(cell2, null);
}

function createEvent(event, cell)
{
	block("#calendar");
	$.ajax({ 
		url: '/event/',
		type: 'GET', 
		cache: false,
		dataType: 'json',
		data: {
			name:	event.name,
			when:	event.when,
			where:	event.where,
			who:	event.who.id,
			repeat: event.repeat
		},
		async: true,
		success: function(data) {
			alert(data + '\n' + data.id);
			event.id = data.id;
			//alert(data.name + data.where + data.when);
		},
		error: function () { 
			alert("error");
		},
		complete: reduce(unblockElement, "#calendar")
	});
}

function modifyEvent()
{
	
}

function setCellData2(cell, name, where, when, who, repeat) {
	cell.innerHTML = name + "<br/>" + where + "<br/>" + who.name;
	cell.data = new EventData();
	cell.data.name = name;
	cell.data.where = where;
	cell.data.when = when;
	cell.data.who = who; 
	cell.data.repeat = repeat;
	$(cell).attr('class', 'calendar_td calendar-data');
}

function setCellData(cell, name, where, when, who, repeat) {
	if (name) {
		//show(who);
		var oldData = cell.data;
		setCellData2(cell, name, where, when, who, repeat);
		if (oldData)
			modifyEvent(oldData, cell.data);
		else
			createEvent(cell.data, cell);
	} else {
		cell.data = null;
		cell.innerHTML = "";
		$(cell).attr('class', 'calendar_td');
	}
}

var form;
var places = "Л1 Л2 Л3 Л4 Л5 Л6 478 479";

function Form(divId) {
	this.div = $('#' + divId)[0];
	this.eventName = $('#event-name', this.div)[0];
	this.eventWhere = $("#event-where", this.div)[0];
	this.eventWhen = $("#event-when", this.div)[0];
	var pl = places.split(' ');
	for (var i = 0; i < pl.length; i++)
		$('<option>' + pl[i] + '</option>').appendTo(this.eventWhere);
	this.eventWho = $('#event-who-select')[0];
	groups = createList(this.eventWho, groups);
	this.eventOnce = $("#event-once", this.div)[0];
	this.eventWeekly = $("#event-weekly", this.div)[0];
	this.eventFortnightly = $("#event-fortnightly", this.div)[0];
}

function noClick() {
	if (form.cell.data) {
		setCellData(form.cell);
	}
	cellDeselect(form.cell);
	unblock(0);
	return false; 
}

function block(el) {
	var a = {
		message: "<img width='64px' height='64px' src='../static/loading.gif'>",
		css: {
			backgroundColor: 'inherit',
	 		color: 'inherit',
	 		border: 'none',
		}
	};
	
	if (el != undefined)
		$(el).block(a);
	else
		$.blockUI(a);
}

function unblockElement(el, t, onUnblock) {
	if (t != undefined)
		$(el).unblock( { fadeOut: t, onUnblock: onUnblock });
	else
		$(el).unblock( { onUnblock: onUnblock });// : { onUnblock: onUnblock });
}

function unblock(t, onUnblock) {
	if (t != undefined)
		$.unblockUI( { fadeOut: t, onUnblock: onUnblock });
	else
		$.unblockUI( { onUnblock: onUnblock });// : { onUnblock: onUnblock });
}

function loadEvents() {
	block();
	$.ajax({ 
		url: '/events/',
		cache: false,
		dataType: 'json',
		async: false,
		success: function(data) {
			//alert(data.places);
			//alert(data.times);
			places = data.places;
			times = data.times;
			dates = data.dates;
			events = data.events;
			for (var i = 0; i < times.length; i++) {
				extend(Time, times[i].start);
				extend(Time, times[i].end);
			}
			for (var i = 0; i < dates.length; i++) {
				extend(Date, dates[i]);
			}
			unblock();
			form = new Form('question');
		},
		error: function () {
			alert("error");
			unblock();
		}
	});
}

function convertDate(t) {
	
}

function createEvent2(event) {
	if (event.status.toLowerCase() == 'canceled')
		return;
	var where = event.where;
	var when = event.when;
	var name = event.name;
	extend(Date, when.start.date);
	extend(Time, when.start.time);
	extend(Time, when.end.time);
	when = new DateTime(when.start.date,
			{ start:when.start.time, end: when.end.time });
	
	for (var i = 0; i < times.length; i++)
		if (when.times.start.compare(times[i].start)) {
			for (var j = 0; j < times.length; j++) {
				if (when.date.compare(dates[j])) {
					setCellData2($('#calendar')[0].cells[i][j],
						name, where, when, '', '');
					return;
				}
			}
		} 
	alert(name + '\n' + where + '\n' + when + '\n' );
}

function getCellDateTime(cell) {
	return new DateTime(dates[cell.xindex], times[cell.yindex]);
}

function yesClick() {
	var repeat = 0;
	if (form.eventWeekly.checked)
		repeat = 7;
	else if (form.eventFortnightly.checked)
		repeat = 14;
	setCellData(form.cell,
		form.eventName.value, 
		form.eventWhere.value,
		getCellDateTime(form.cell),
		groups[form.eventWho.value],
		repeat);//selectedIndex]
	
	unblock(0, function() {});
	/*block();
 	setTimeout(function() {
		$.ajax({ 
			url: 'wait.html', 
			cache: false, 
			success: function() { 
				unblock();
			},
			error: function() { 
				unblock();
				cellDeselect(form.cell); 
			}
		});
	}, 1000);
	*/
}

function createCalendars(id) {
	var div = $('#' + id);
	var sel = div.find('select');
	sel.attr('size', calendars.length);
	for (var i = 0; i < calendars.length; i++) {
		var opt = $('<option>' + calendars[i].name + '</option>');
		opt.appendTo(sel);
		opt.attr('value', calendars[i]);
	}
	div.show();
	div.find('#new-calendar-submit').click(newCalendar);
	div.find('#save-calendar').click(saveCalendar);
}

function saveCalendar() {
	var sel = $('#calendars').find('select');
	var i = sel.attr('selectedIndex');
	$.ajax({ 
		url: '/calendars/',
		dataType: 'json',
		data: { id: calendars[i].id },
		cache: false, 
		success: function() {
		},
		error: function() { 
			alert('error');
		}
	});
}

function newCalendar() {

}