
function Tree(div) {
	this.newGroup = null;
	this.renamedGroup = null;
	this.selectedGroup = null;
	this.nodes = [];
	this.div = div;
	this.selectListeners = [];
	this.nodeSelected = function (listener) {
		this.selectListeners.push(listener);
	}
	this.fireSelect = function () {
		for (var i = 0; i < this.selectListeners.length; i++)
			this.selectListeners[i](this.selectedGroup);
	}
}

var tree = null;

function displayLinks(g, d) {
	if (!g.div.dropping)
		g.node().children('.links').css('display', d);
}

function showLinks(g) {
	displayLinks(g, 'inline');
}

function hideLinks(g) {
	displayLinks(g, 'none');
}

function nodeMouseover(g) {
	if (!g.selected && !g.div.dropping)
		g.nodeName().css('background-color', '#eee');
}

function nodeMouseout(g) {
	if (!g.selected && !g.div.dropping)
		g.nodeName().css('background-color', '#fff');
}

function selectGroup(g) {
	if (g.tree.selectedGroup)
	{
		g.tree.selectedGroup.nodeName().css('background-color', 'inherit');
		g.tree.selectedGroup.selected = false;
	}
	var fire = g != g.tree.selectedGroup;
	g.tree.selectedGroup = g;
	g.selected = true;
	g.nodeName().css('background-color', '#cdf');
	if (fire)
		g.tree.fireSelect();
}

function expandNode2(g, open) {
	var node = g.node();
	var children = $(g.div).children('.children');
	var img = g.tree.treeImages;
	var e = $(node).children('.expand');
	if (!open) {
		//children.css('display', 'none');
		children.slideUp("fast");
		if (img)
			e.attr('src', img.closed);
		else
			e.html('+');
	} else {
		//children.css('display', 'block');
		children.slideDown("fast");
		if (img)
			e.attr('src', img.opened);
		else
			e.html('-');
	}
}

function expandNode(g, open, continuation) {
	if (open && !g.loaded) {
		var src = g.nodeIcon().attr('src');
		g.nodeIcon().attr('src', g.tree.treeImages.loading);
		jsonGet('/groups/' + g.id + '/', {},
			function(groups) {
				//show(groups);
				for (var i = 0; i < groups.length; i++) {
					groups[i].children = [];
					groups[i].loaded = groups[i].type != 'group';
					groups[i].parentGroup = g;
					groups[i].tree = g.tree;
					g.children.push(groups[i]);
					createGroupDiv(groups[i]).appendTo(
							$(g.div).children('.children'));
				}
				if (g.children.length > 0)
					expandNode2(g, open);
				else
					g.expandImage().attr('src', g.tree.treeImages.empty);
				g.loaded = true;
			}, 
			function() {
				alert('error');
			},
			function() {
				g.nodeIcon().attr('src', src);
				if (continuation)
					continuation();
			}
		); 
	} else {
		expandNode2(g, open);
		if (continuation)
			continuation();
	}
}

function expandCollapse(g) {
	if (g.loaded && (!g.children || g.children.length == 0))
		return;

	selectGroup(g);
	expandNode(g, $(g.div).children('.children').css('display') == 'none');
}

function Ev() {
	this.listeners = [];
}

function Group() {
	this.node = function () {
		return $(this.div).children('.node');
	}
	this.nodeName = function () {
		return $(this.div).children('.node').children('.name');
	}
	this.expandImage = function () {
		return $(this.div).children('.node').children('.expand');
	}
	this.nodeIcon = function () {
		return $(this.div).children('.node').children('.icon');
	}
}

function createGroupDiv(g) {
	var div = $(
		'<div class="group"><div class="node">' + 
		(g.tree.treeImages 
			? '<img src="' + (!g.loaded
					? g.tree.treeImages.closed 
					: g.tree.treeImages.empty) +
				'" class="expand"/>'
			: '<span class="expand">&nbsp;</span>') +
		'<img class="icon"/>' +
		'<span class="name">' + g.name + '</span>' +
		'</div>' + 
		'<div class="children"></div></div>');
	g.div = div[0];
	div[0].data = g;
	extend(Group, g);
	var node = g.node();
	if (g.tree.dndEnabled) {
		node.draggable({
			revert: true,
			zIndex: 1000,
			//cursorAt: { left: 0, top: 0 },
			distance: 10,
			opacity: 0.5,
			helper: 'clone'
		});
		node.droppable({
			hoverClass: 'drop-hover',
	    	over: function(event, ui) {
	    		$(this).parent().dropping = true;
	    		$(this).children('.name').css('background-color', '#128');
			},
			out: function(event, ui) {
				$(this).parent().dropping = false;
	    		$(this).children('.name').css('background-color', '#fff');
			},
			drop: function(event, ui) {
				var pdiv = ui.draggable.parent()[0];
				var gg = pdiv.data;
				moveGroup(gg, g)
			}
	    });
	}
	if (!g.tree.readOnly) {
		var links = $('.groupLinks').clone();
		links.removeClass('groupLinks');
		links.appendTo(node);
		
		$(node).mouseover(reduce(showLinks, g));
		$(node).mouseout(reduce(hideLinks, g));
		hideLinks(g);
	}
	
	$(node).click(reduce(selectGroup, g));
	$(node).mouseover(reduce(nodeMouseover, g));
	$(node).mouseout(reduce(nodeMouseout, g));
	
	$(node).find('.expand').click(reduce(expandCollapse, g));
	$(node).children('.name').dblclick(reduce(expandCollapse, g));
	
	if (!g.tree.readOnly) {
		$(node).find('.new').click(reduce(startNewGroup, g));
		$(node).find('.del').click(reduce(deleteGroup, g));
		$(node).find('.rename').click(reduce(startRenameGroup, g));
		$(node).find('.new-user').click(reduce2(startNewGroup, g, 'user'));
	}
	
	if (g.tree.treeImages) 
		$(node).find('.icon').attr('src', 
				g.tree.treeImages[g.type == undefined ? 'group' : g.type]);
	
	return div;
}

function moveGroup(g, pg) {
	expandNode(g, true, function() {
		removeGroup(g);
		pg.children.push(g);
		g.parentGroup = pg;
		
		$(g.div).remove();
		$(g.div).appendTo($(pg.div).children('.children')[0]); 
	});
}

function createGroup(pg, g, div) {
	div.remove();
	var name = $(div).children("input")[0].value;
	var g = { name: name, parent: pg.id, id: null, children: [], type: g.type };
	g.tree = pg.tree;
	pg.children.push(g);
	g.parentGroup = pg;
	div = createGroupDiv(g);
	g.div = div;
	div.tree = pg.div.tree; 
	div.appendTo($(pg.div).find('.children')[0]);

	expandNode(pg, true);
	//$(pg.div).children('span').children('.expand').html(
	//	($(pg.div).children('.children').css('display') == 'none') ? '+' : '-');

	block(g.tree.div, 0, 300);
	jsonGet(
		'/groups_post/', 
		{ name: g.name, id: pg.id, type: g.type },
		function(data) {
			//alert(data ? data.id : data);
			g.id = data.id;
		},
		function () { 
			alert("error");
		},
		reduce2(unblockElement, g.tree.div, 0)
	);
	return false;
}

function cancelNewGroup(ng) {
	$(ng.div).remove();
	ng.tree.newGroup = null;
	return false;
}

function createNewGroupDiv(g, ng) {
	var div = $('<div class="group">' + 
		'<img class="expand" src="' + g.tree.treeImages.empty + '"/>' + 
		'<img class="icon"/>' + 
		'<input type="text" value="' + ng.name + '"/>&nbsp;' + 
		'<a href="#"><img src="/static/save.gif" align="center"/></a>&nbsp;' + 
		'<a href="#"><img src="/static/delete.gif" align="center"/></a></div>');
	$(div.find('a')[0]).click(reduce3(createGroup, g, ng, div));
	$(div.find('a')[1]).click(reduce3(cancelNewGroup, ng));
	div.data = ng;
	ng.div = div;
	if (g.tree.treeImages) 
		$(div).find('.icon').attr('src', 
				ng.tree.treeImages[ng.type == undefined ? 'group' : ng.type]);
	return div;
}

function startNewGroup(g, type) {
	if (g.tree.renamedGroup) {
		cancelRenameGroup(g.tree.renamedGroup);
	}
	if (g.tree.newGroup != null)
		g.tree.newGroup.div.remove();
	selectGroup(g);
	type = !type ? 'group' : type;
	expandNode(g, open, function() {
		var ng = {
			name: 'new ' + type, 
			parent:	g.id, 
			id: null, 
			tree: g.tree, 
			type: type
		};
		g.tree.newGroup = ng;
		var div = createNewGroupDiv(g, ng);
		div.appendTo($(g.div).find('.children')[0]);
		$(g.div).children('.children').css('display', 'block');
		//div.children('input')[0].focus();
	});
	return false;
}

function indexOf(a, o) {
	for (var i = 0; i < a.length; i++)
		if (a[i] == o)
			return i;
	return -1;
}

function removeGroup(g) {
	if (g.parentGroup) {
		g.parentGroup.children.splice(
			indexOf(g.parentGroup.children, g), 1);

		if (g.parentGroup.children.length <= 0) {	
			var img = g.tree.treeImages;
			var exp = g.parentGroup.expandImage();
			if (img)
				exp.attr('src', img.empty); 
			else
				exp.html('&nbsp;');
		}
	}
}

function deleteGroup(g) {
	$(g.div).remove();
	removeGroup(g);
	block(g.tree.div, 0, 300);
	$.ajax({
		url: '/groups_delete/',
		type: 'GET', 
		cache: false,
		dataType: 'json',
		data: { id: g.id },
		async: true,
		success: function(data) {
		},
		error: function () { 
			alert("error");
		},
		complete: reduce2(unblockElement, g.tree.div, 0)
	});
	return false;
}

function startRenameGroup(g) {
	if (g.tree.renamedGroup)
		cancelRenameGroup(g.tree.renamedGroup);
	if (g.tree.newGroup)
	{
		cancelNewGroup(g.tree.newGroup);
		g.tree.newGroup = null;
	}
	g.tree.renamedGroup = g;
	selectGroup(g);
	var name = g.nodeName();
	//name.css('background-color', '#fff');
	name.html(
		'<input type="text" id="newname" value="' + g.name + '"/>' +
		'<a href="#" class="ok"><img src="' + g.tree.treeImages.save + '" align="center"/></a>&nbsp;' + 
		'<a href="#" class="cancel"><img src="' + g.tree.treeImages.del + '" align="center"/></a>');
	name.children('.ok').click(reduce(renameGroup, g));
	name.children('.cancel').click(reduce(cancelRenameGroup, g));
	return false;
}

function cancelRenameGroup(g) {
	 g.nodeName().html(g.name);
	 g.tree.renamedGroup = null;
	 return false;
}

function saveGroup(g) {
	block(g.tree.div, 0, 300);
	jsonGet(
		'/groups_put/',
		{ id: g.id, name: g.name, email: g.email, calId: g.calId },
		function (data) {
			//show(data);
		},
		function () { 
			alert("error");
		},
		reduce2(unblockElement, g.tree.div, 0)
	);
}

function renameGroup(g) {
	var name = $(g.div).find('#newname')[0].value;
	g.name = name;
	g.node().children('.name').html(g.name);
	saveGroup(g);
	return false;
}

function saveSelectedGroup(tree) {
	saveGroup(tree.selectedGroup);
}


function createTree2(id, g) {
	var div = createGroupDiv(g);
	div[0].tree = $(id)[0];
/*	if (g.children) {
		if (g.children.length > 0)
			expandNode(g, false);
		for (var i = 0; i < g.children.length; i++) {
			createTree2(id, g.children[i]).appendTo(
					$(div).children('.children'));
		}
	}
*/
	return div;
}

function createTree1(groups, tree) {
	var t = {};
	for (var i = 0; i < groups.length; i++) {
		var g = groups[i];
		t[g.id] = g;
		g.children = [];
		g.tree = tree;
		if (!g.type)
			g.type = 'group';
	}
	
	for (var i = 0; i < groups.length; i++) {
		var g = groups[i];
		if (g.parent == null) {
			tree.nodes.push(g);
		} else {
			g.loaded = false;
			var pg = t[g.parent];
			if (!pg)
				continue;
			if (!pg.children)
				pg.children = [];
			pg.children.push(g);
			g.parentGroup = pg;
		}
	}
	return t;
}

function createTree(groups, id, images, readOnly) {
	var div = $(id)[0];
	var tree = new Tree(div);
	tree.treeImages = images;
	tree.readOnly = readOnly ? true : false;
	div.tree = tree;
	
	createTree1(groups, tree);
	for (var i = 0; i < tree.nodes.length; i++)
		createTree2(id, tree.nodes[i]).appendTo(div);
	return tree;
}

function createList2(select, g, n) {
	var padding = "";
	for (var i = 0; i < n; i++)
		padding += "&nbsp;";
	var opt = $('<option>' + padding + g.name + '</option>');
	opt.appendTo(select);
	opt.attr('value', g.id);
	if (g.children)
		for (var i = 0; i < g.children.length; i++)
			createList2(select, g.children[i], n + 4);
}

function createList(id, groups, images) {
	var select = $(id)[0];
	var tree = { nodes: [] };
	var g = createTree1(groups, tree);
	for (var i = 0; i < tree.nodes.length; i++)
		createList2(select, tree.nodes[i], 0);
	return g;
}
