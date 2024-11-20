function Game(config) {
	this.config = config;
	this.canvas_width = 1000;
	this.canvas_height = 900;
	this.cnt_squares = 10;
	this.square_size = 40;
	this.y_grids = 20;
	this.x_grid_left = 60;
	this.x_grid_right = this.x_grid_left + this.cnt_squares*this.square_size + 100;

	this.list_shiptypes = [
		{ 'is_vertical': false, 'i': 1, 'j': 12-0.5, 'length': 5, 'ship_name': "carrier" },
		{ 'is_vertical': false, 'i': 1, 'j': 13-0.5, 'length': 4, 'ship_name': "battleship" },
		{ 'is_vertical': false, 'i': 1, 'j': 14-0.5, 'length': 3, 'ship_name': "cruiser" },
		{ 'is_vertical': false, 'i': 1, 'j': 15-0.5, 'length': 3, 'ship_name': "submarine" },
		{ 'is_vertical': false, 'i': 1, 'j': 16-0.5, 'length': 2, 'ship_name': "destroyer" },
		{ 'is_vertical': true,  'i': 8, 'j': 12-0.5, 'length': 5, 'ship_name': "carrier" },
		{ 'is_vertical': true,  'i': 7, 'j': 13-0.5, 'length': 4, 'ship_name': "battleship" },
		{ 'is_vertical': true,  'i': 6, 'j': 14-0.5, 'length': 3, 'ship_name': "cruiser" },
		{ 'is_vertical': true,  'i': 5, 'j': 14-0.5, 'length': 3, 'ship_name': "submarine" },
		{ 'is_vertical': true,  'i': 4, 'j': 15-0.5, 'length': 2, 'ship_name': "destroyer" }
	];

	this.dict_colors = {
		1: 'rgb(0,220,0)',
		2: 'magenta',
		3: 'black',
	}
	this.dict_players_colors = [
		'blue',
		'green',
		'red',
		'rgb(255, 204, 0)',
	]

	this.player_state = null;
	this.selection_state = null;
	this.idx_player_you = 0;
	this.dict_area_rect = null;
	this.ID_BUTTON_SUBMIT = 'submit';
	this.dict_imgs = null;

	this.init();
}

Game.prototype.init = function () {
	this.canvas = document.getElementById(this.config.canvas_id);
	this.ctx = this.canvas.getContext("2d");
	this.canvas.width = this.canvas_width;
	this.canvas.height = this.canvas_height;
	this.bind_events();
	this.render();
}

Game.prototype.get_rect = function (x, i, j, length, is_vertical) {
	var rect = [];
	rect[0] = x + i*this.square_size;
	rect[1] = this.y_grids + j*this.square_size + this.square_size*2;
	if(is_vertical) {
 		rect[2] = this.square_size;
 		rect[3] = length*this.square_size;
	} else {
 		rect[2] = length*this.square_size;
 		rect[3] = this.square_size;
	}
	return rect;
}

Game.prototype.calc_objects_rect = function () {

	// shiptypes
	var player = this.player_state.players[this.player_state.idx_player_you];
	for(var i=0; i<this.list_shiptypes.length; i++) {
		var shiptype = this.list_shiptypes[i];
		shiptype.rect = this.get_rect(this.x_grid_left, shiptype.i, shiptype.j, shiptype.length, shiptype.is_vertical);
		shiptype.is_hidden = false;
		let num_3_ships_set = 0;
		for(var j=0; j<player.ships.length; j++) {
			var ship = player.ships[j];
			if(shiptype.length==ship.length && ship.location!=null) {
				shiptype.is_hidden = true;
				if(ship.length==3) {
					num_3_ships_set++
				}
			}
		}
		if(shiptype.length==3 && num_3_ships_set!=2) {
			shiptype.is_hidden = false;
		}

	}

	this.dict_area_rect= {};



	// submit button
	var x = this.cnt_squares*this.square_size/2;
	if(this.player_state.phase == 'setup') {
		x += this.x_grid_left;
	} else {
		x += this.x_grid_right;
	}
	var y = this.y_grids + 12.5*this.square_size;
	var txt = 'Submit';
	var f = 24;
	var dx = 20;
	var dy = 10;
	this.ctx.font = f+'px Arial';
	var w = this.ctx.measureText(txt).width;
	this.dict_area_rect[this.ID_BUTTON_SUBMIT] = {
		'rect': [
			x-dx-w/2,
			y,
			w+dx*2,
			f+dy*2
		],
		'f': f,
		'txt': txt,
		'dx': dx,
		'dy': dy,
	}
}

Game.prototype.bind_events = function() {
	this.canvas.onmousemove = this.on_mouse_move.bind(this);
	this.canvas.onmousedown = this.on_mouse_down.bind(this);
}

Game.prototype.set_player_state = function(player_state) {
	console.log(player_state)
	this.player_state = this.transform_state(player_state);

	this.selection_state = {
		'i_shiptype_hovered': null,
		'i_shiptype_selected': null,
		'i_ship_hovered': null,
		'i_ship_selected': null,
		'i_target_hovered': null,
		'i_target_selected': null,
		'submit_button_state': null,
	}

	/*
	this.selection_state = {
		'idx_card_hover': null,
		'idx_card_selected': null,
		'pos_from_selected': null,
		'idx_pos_hover': null,
		'idx_exchange_card_hover': null,
		'idx_exchange_card_selected': null,
		'pos_to_selected': null,
		'exchange_card_visible': false,
		'submit_button_state': null,
	};
	this.list_card_selectable = [];
	this.list_ball_selectable_from = [];
	this.list_ball_selectable_to = [];
	this.player_state = player_state;
	//this.player_state.list_player[0].list_id_card[2] = 'JKR';
	//this.player_state.list_player[0].list_id_card[3] = '2_H';
	
	this.calc_board_rotation();
	*/

	this.calc_objects_rect();
	this.calc_selectable();
	this.render();

	if(false && this.player_state.phase=='setup' && !this.config.spectator && this.player_state.idx_player_active==this.player_state.idx_player_you && this.player_state.list_action.length>0) {
		var i = Math.floor(Math.random()*this.player_state.list_action.length);
		var action = this.player_state.list_action[i];
		this.send_action_callback(action);
		return;
	}
}

Game.prototype.get_ij = function (location) {
	return [
		location.toLowerCase().charCodeAt(0)-97,
		parseInt(location.substr(1))-1
	];
}

Game.prototype.transform_state = function (raw_state) {

	if(raw_state.selected_action!=null) {
		var action = raw_state.selected_action;
		if(action.action_type == 'set_ship') {
			var ij = this.get_ij(action.location[0]);
			action.i = ij[0];
			action.j = ij[1];
			action.is_vertical = action.location[0].substr(0,1) == action.location[1].substr(0,1);
			action.length = action.location.length;
			var x = raw_state.idx_player_active==0 ? this.x_grid_left : this.x_grid_right;
			action.rect = this.get_rect(x, action.i, action.j, action.length, action.is_vertical);
		}
	}

	if(raw_state.list_action!=null) {
     	for(var i=0; i<raw_state.list_action.length; i++) {
			var action = raw_state.list_action[i];
			var ij = this.get_ij(action.location[0]);
			action.i = ij[0];
			action.j = ij[1];
			if(action.action_type == 'set_ship') {
				action.is_vertical = action.location[0].substr(0,1) == action.location[1].substr(0,1);
				action.length = action.location.length;
				action.rect = this.get_rect(this.x_grid_left, action.i, action.j, action.length, action.is_vertical);
			} else if(action.action_type == 'shoot') {
				action.rect = this.get_rect(this.x_grid_right, action.i, action.j, 1, action.is_vertical);
			}
		}
	}

 	for(var p=0; p<raw_state.players.length; p++) {
		var player = raw_state.players[p];
		// ships
     	for(var i=0; i<player.ships.length; i++) {
			var ship = player.ships[i];
			if(ship.location!=null) {
				var ij = this.get_ij(ship.location[0]);
				ship.i = ij[0];
				ship.j = ij[1];
				ship.is_vertical = ship.location[0].substr(0,1) == ship.location[1].substr(0,1);
				ship.length = ship.location.length;
			}
		}
		// shots
     	for(var i=0; i<player.shots.length; i++) {
			var shot = player.shots[i];
			var successfull = player.successful_shots.includes(shot);
			var ij = this.get_ij(shot);
			player.shots[i] = {
				'location': shot,
				'i': ij[0],
				'j': ij[1],
				'successfull': successfull,
			}
		}
	}
	return raw_state;
}


Game.prototype.calc_board_rotation = function() {
	// rotate xy of pos, pos numbering remains the same
	this.list_xy_pos_rotated = [];
	for(var idx=0; idx<this.CNT_STEPS; idx++) {
		var idx_to = (idx + this.CNT_STEPS - this.player_state.idx_player_you*16) % this.CNT_STEPS;
		this.list_xy_pos_rotated[idx_to] = this.list_xy_pos[idx];
	}
	for(var idx=this.CNT_STEPS; idx<this.CNT_POS; idx++) {
		var idx_to = this.CNT_STEPS + (idx + 32 - this.player_state.idx_player_you*8) % 32;
		this.list_xy_pos_rotated[idx_to] = this.list_xy_pos[idx];
	}

	// rotate players in this.player_state.list_player so that you are at 0
	var list_player = [];
	for(var idx=0; idx<4; idx++) {
		var idx_to = (idx + this.player_state.idx_player_you) % 4;
		list_player[idx_to] = this.player_state.list_player[idx];
		list_player[idx_to].idx_orig = idx;
	}
	this.player_state.list_player = list_player;
}


Game.prototype.calc_objects_rect_dog = function() {
	this.dict_player_card_rect = {};

	var card_w = 0.3*500;
	var card_h = 0.3*726;
	var card_padding = 50;

	// cards center
	var card_x = this.board_center_x - 150;
	var card_y = this.board_center_y - 110;
	this.dict_player_card_rect.card_stack = [card_x+card_w+5, card_y, card_w, card_h];
	this.dict_player_card_rect.card_pile = [card_x, card_y, card_w, card_h];

	function sortCards(a,b) {
		return this.dict_id_card_nr[a] - this.dict_id_card_nr[b];
	}
	function sortEchangeCards(a,b) {
		return this.dict_id_card_nr[a.id_card] - this.dict_id_card_nr[b.id_card];
	}

	// sort players cards
	for(var p=0; p<4; p++) {
		var player = this.player_state.list_player[p];
		player.list_id_card.sort(sortCards.bind(this));
	}

	// cards players
	this.dict_player_card_rect.list_player = []
	for(var p=0; p<4; p++) {
		this.dict_player_card_rect.list_player[p] = [];
		if(p%2==0) {
			for(var i=0; i<this.player_state.list_player[p].list_id_card.length; i++) {
				card_x = this.board_center_x - (this.player_state.list_player[p].list_id_card.length*(card_w + 10) - 10)/2 + i*(card_w + 10);
				if(p==0) {
					card_y = this.board_y + this.board_width + card_padding;
				} else {
					card_y = this.board_y - card_padding - card_h;
				}
				this.dict_player_card_rect.list_player[p][i] = [card_x, card_y, card_w, card_h];
			}
		} else {
			for(var i=0; i<this.player_state.list_player[p].list_id_card.length; i++) {
				card_y = this.board_center_x + (this.player_state.list_player[p].list_id_card.length*(card_w + 10) - 10)/2 - i*(card_w + 10) - card_w;
				if(p==1) {
					card_x = this.board_y + this.board_width + card_padding;
				} else {
					card_x = this.board_y - card_padding - card_h;
				}
				this.dict_player_card_rect.list_player[p][i] = [card_x, card_y, card_h, card_w];
			}
		}
	}

	// exchange cards
	this.dict_exchange_card_rect = [];
	for(var i=0; i<this.player_state.list_action.length; i++) {
		var action = this.player_state.list_action[i];
		if(action.id_card.indexOf('JKR>')==0) {
     		var id_card = action.id_card.substr('JKR>'.length);
     		this.dict_exchange_card_rect.push({
     			'id_card': id_card,
     		});
		}
	}
	// sort exchange cards
	this.dict_exchange_card_rect.sort(sortEchangeCards.bind(this));
	// calc rect
	for(var i=0; i<this.dict_exchange_card_rect.length; i++) {
		var exchange_card = this.dict_exchange_card_rect[i];
		card_x = this.board_center_x - (this.dict_exchange_card_rect.length*(card_w/2 + 10) - 10)/2 + i*(card_w/2 + 10);
		card_y = this.board_y + this.board_width + card_h + card_padding + 10;
		exchange_card.rect = [card_x, card_y, card_w/2, card_h/2];
	}

	this.dict_area_rect = {};

	// submit button
	var txt = 'Submit';
	var f = 24;
	var dx = 20;
	var dy = 20;
	this.ctx.font = f+'px Arial';
	var w = this.ctx.measureText(txt).width;
	this.dict_area_rect[this.ID_BUTTON_SUBMIT] = {
		'rect': [
			this.board_center_x-w/2-dx,
			this.board_center_y+this.board_width*0.85,
			w+dx*2,
			f+dy*2
		],
		'f': f,
		'txt': txt,
		'dx': dx,
		'dy': dy,
	}

	// area cards
	var w = (card_w+10)*6;
	this.dict_area_rect[this.ID_AREA_CARDS] = {
		'rect': [
			this.board_center_x-w/2,
			this.board_y + this.board_width + card_padding - 5,
			w,
			card_h + 10
		],
	}

	// area cards
	var x = 0;
	var y = 0;
	var w = 0;
	var h = 0;
	if(this.dict_exchange_card_rect.length>0) {
		x = this.dict_exchange_card_rect[0].rect[0]-5;
		y = this.dict_exchange_card_rect[0].rect[1];
		w = (this.dict_exchange_card_rect[0].rect[2]+10)*this.dict_exchange_card_rect.length;
		h = this.dict_exchange_card_rect[0].rect[3];
	}
	this.dict_area_rect[this.ID_AREA_EXCHANGE_CARDS] = {
		'rect': [
			x,
			y,
			w,
			h
		],
	}

	// area board
	this.dict_area_rect[this.ID_AREA_BOARD] = {
		'rect': [
			this.board_x,
			this.board_y,
			this.board_width,
			this.board_width
		],
	}

}

Game.prototype.calc_selectable = function() {
 	if(this.config.spectator || this.player_state.idx_player_active!=this.player_state.idx_player_you) {
 		return;
 	}


 	if(this.player_state.phase == 'setup') {

 		// ships
     	for(var s=0; s<this.list_shiptypes.length; s++) {
			var ship = this.list_shiptypes[s];

			var is_selectable = false;
			for(var i=0; i<this.player_state.list_action.length; i++) {
				var action = this.player_state.list_action[i];
				if(ship.length == action.length && ship.is_vertical == action.is_vertical) {
					is_selectable = true;
					break;
				}
			}
			ship.is_selectable = is_selectable;
		}

		// actions
		if(this.selection_state.i_shiptype_selected!=null) {
			var ship_selected = this.list_shiptypes[this.selection_state.i_shiptype_selected];
			for(var i=0; i<this.player_state.list_action.length; i++) {
				var action = this.player_state.list_action[i];
				action.is_selectable = ship_selected.length == action.length && ship_selected.is_vertical == action.is_vertical;
			}
		}

		if(this.selection_state.i_ship_selected!=null) {
			this.selection_state.submit_button_state = 1;
		}	

	}

}


Game.prototype.on_mouse_move = function(e) {
 	if(this.can_select()) return;

 	var xy = this.get_xy_from_cursor(e);
 	var do_render = false;


	if(this.player_state.phase == 'setup') {

		// shiptype
 		var i_shiptype_hovered_before = this.selection_state.i_shiptype_hovered;
 		var i_shiptype_hovered = null;
     	for(var i=0; i<this.list_shiptypes.length; i++) {
			var ship = this.list_shiptypes[i];
			if(!ship.is_selectable) continue;
     		if(this.is_point_in_rect(xy, ship.rect) && i_shiptype_hovered==null) {
     			i_shiptype_hovered = i;
     		}
		}
		this.selection_state.i_shiptype_hovered = i_shiptype_hovered;
		do_render |= i_shiptype_hovered_before!=this.selection_state.i_shiptype_hovered;

		// ship
 		var i_ship_hovered_before = this.selection_state.i_ship_hovered;
 		var i_ship_hovered = null;
     	for(var i=0; i<this.player_state.list_action.length; i++) {
			var action = this.player_state.list_action[i];
			if(!action.is_selectable) continue;
     		if(this.is_point_in_rect(xy, action.rect) && i_ship_hovered==null) {
     			i_ship_hovered = i;
     		}
		}
		this.selection_state.i_ship_hovered = i_ship_hovered;
		do_render |= i_ship_hovered_before!=this.selection_state.i_ship_hovered;

	} else if(this.player_state.phase == 'running') {

		// targets
 		var i_target_hovered_before = this.selection_state.i_target_hovered;
 		var i_target_hovered = null;
		for(var i=0; i<this.player_state.list_action.length; i++) {
			var action = this.player_state.list_action[i];
     		if(this.is_point_in_rect(xy, action.rect) && i_target_hovered==null) {
     			i_target_hovered = i;
     		}
		}
		this.selection_state.i_target_hovered = i_target_hovered;
		do_render |= i_target_hovered_before!=this.selection_state.i_target_hovered;

	}

 	// check submit button
 	if(this.selection_state.submit_button_state!=null) {
     	var submit_button_state_before = this.selection_state.submit_button_state;
     	this.selection_state.submit_button_state = this.get_id_button_from_xy(xy) == this.ID_BUTTON_SUBMIT ? 2 : 1;
     	do_render |= submit_button_state_before!=this.selection_state.submit_button_state;
 	}

 	if(do_render) {
 		this.render();
 	}
}

Game.prototype.on_mouse_down = function(e) {
 	if(this.can_select()) return;

 	var xy = this.get_xy_from_cursor(e);

	if(this.player_state.phase == 'setup') {


     	// check submit button
     	/*if(this.selection_state.submit_button_state!=null) {
	     	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_BUTTON_SUBMIT].rect)) {
		     	var id_button = this.get_id_button_from_xy(xy);
		     	if(id_button==this.ID_BUTTON_SUBMIT) {
		     		var action = this.player_state.list_action[this.selection_state.i_ship_selected];
			     	this.send_action_callback(action);
			     	return;
		     	}
		    }
		}*/

		// ship
		var i_ship_selected = null;
     	for(var i=0; i<this.player_state.list_action.length; i++) {
			var action = this.player_state.list_action[i];
			if(!action.is_selectable) continue;
     		if(this.is_point_in_rect(xy, action.rect) && i_ship_selected==null) {
     			i_ship_selected = i;
     		}
		}
		this.selection_state.i_ship_selected = i_ship_selected;

		// shiptype
 		var i_shiptype_selected = null;
     	for(var i=0; i<this.list_shiptypes.length; i++) {
			var ship = this.list_shiptypes[i];
			if(!ship.is_selectable) continue;
     		if(this.is_point_in_rect(xy, ship.rect) && i_shiptype_selected==null) {
     			i_shiptype_selected = i;
     		}
		}

		if(i_ship_selected==null) {
			this.selection_state.i_shiptype_selected = i_shiptype_selected;
		} 

		if(this.selection_state.i_ship_selected!=null) {
			//this.selection_state.submit_button_state = 1;
     		var action = this.player_state.list_action[this.selection_state.i_ship_selected];
	     	this.send_action_callback(action);
		} else {
			this.selection_state.submit_button_state = null;
		}

	} else if(this.player_state.phase == 'running') {


     	// check submit button
     	/*if(this.selection_state.submit_button_state!=null) {
	     	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_BUTTON_SUBMIT].rect)) {
		     	var id_button = this.get_id_button_from_xy(xy);
		     	if(id_button==this.ID_BUTTON_SUBMIT) {
		     		var action = this.player_state.list_action[this.selection_state.i_target_selected];
			     	this.send_action_callback(action);
			     	return;
		     	}
		    }
		}*/


		// targets
 		var i_target_selected = null;
		for(var i=0; i<this.player_state.list_action.length; i++) {
			var action = this.player_state.list_action[i];
     		if(this.is_point_in_rect(xy, action.rect) && i_target_selected==null) {
     			i_target_selected = i;
     		}
		}
		this.selection_state.i_target_selected = i_target_selected;

		if(this.selection_state.i_target_selected!=null) {
			//this.selection_state.submit_button_state = 1;
     		var action = this.player_state.list_action[this.selection_state.i_target_selected];
	     	this.send_action_callback(action);
	     	return;

		} else {
			this.selection_state.submit_button_state = null;
		}

	}

 	this.calc_selectable()

 	this.render();
}

Game.prototype.send_action_callback = function(action) {	
}

Game.prototype.can_select = function(e) {
 	return this.player_state==null || this.selection_state==null || this.player_state.idx_player_active!=this.player_state.idx_player_you;
}

Game.prototype.get_xy_from_cursor = function(e) {
 	var x = e.offsetX || (e.pageX - this.canvas.offsetLeft);
 	var y = e.offsetY || (e.pageY - this.canvas.offsetTop);
 	return [x, y];
}

Game.prototype.get_idx_card_from_xy = function(xy) {
 	var idx_card = null;
 	var player = this.player_state.list_player[this.idx_player_you];
 	for(var i=0; i<player.list_id_card.length; i++) {
 		if(!this.list_card_selectable[i]) {
 			continue;
 		}
 		var card = this.dict_player_card_rect.list_player[this.idx_player_you][i];
 		if(this.is_point_in_rect(xy, card)) {
 			idx_card = i;
 			break;
 		}
 	}
 	return idx_card;
}

Game.prototype.get_idx_exchange_card_from_xy = function(xy) {
 	var idx_card = null;
 	for(var i=0; i<this.dict_exchange_card_rect.length; i++) {
 		var card = this.dict_exchange_card_rect[i];
 		if(this.is_point_in_rect(xy, card.rect)) {
 			idx_card = i;
 			break;
 		}
 	}
 	return idx_card;
}

Game.prototype.get_id_button_from_xy = function(xy) {
	var button = this.dict_area_rect[this.ID_BUTTON_SUBMIT];
	if(this.is_point_in_rect(xy, button.rect)) {
		return this.ID_BUTTON_SUBMIT;
	}
 	return null;
}

Game.prototype.get_idx_pos_from_xy = function(xy) {
 	var idx_pos = null;
 	for(var i=0; i<this.CNT_POS; i++) {
 		var xy_pos = this.list_xy_pos_rotated[i];
 		if(this.is_point_in_circle(xy, xy_pos, this.r_active)) {
 			idx_pos = i;
 			break;
 		}
 	}
 	return idx_pos;
}

Game.prototype.is_point_in_rect = function(xy, rect) {
	return xy[0]>rect[0] && xy[0]<rect[0]+rect[2] && xy[1]>rect[1] && xy[1]<rect[1]+rect[3];
}
Game.prototype.is_point_in_circle = function(xy, xy_center, r) {
	return (xy[0]-xy_center[0])**2 + (xy[1]-xy_center[1])**2 < r**2;
}


Game.prototype.render_grid = function (title, x_top_left, y_top_left) {

	// Title
	this.ctx.fillStyle = 'black';
	this.ctx.textBaseline = 'top';
	this.ctx.font = 'bold 24px Arial';
	this.ctx.fillText(title, x_top_left, y_top_left);

	y_top_left += this.square_size*2;

	// Background
		var x = x_top_left;
		var y = y_top_left;
		var w = this.cnt_squares*this.square_size;
		var h = this.cnt_squares*this.square_size;
	this.ctx.fillStyle = 'white';//'rgba(230,230,255)';
	this.ctx.fillRect(x, y, w, h);

	// Grid
	this.ctx.lineWidth = 1;
	this.ctx.strokeStyle = 'black';
	this.ctx.fillStyle = 'black';
	this.ctx.font = '20px Arial';
	this.ctx.textBaseline = 'middle';
 	for(var i=0; i<this.cnt_squares+1; i++) {
 		var x = x_top_left + i*this.square_size + 0.5;
 		var y1 = y_top_left;
 		var y2 = y_top_left + this.cnt_squares*this.square_size;
 		this.ctx.beginPath();
 		this.ctx.moveTo(x,y1);
 		this.ctx.lineTo(x,y2);
 		this.ctx.stroke();
 		var y = y_top_left + i*this.square_size + 0.5;
 		var x1 = x_top_left;
 		var x2 = x_top_left + this.cnt_squares*this.square_size;
 		this.ctx.beginPath();
 		this.ctx.moveTo(x1,y);
 		this.ctx.lineTo(x2,y);
 		this.ctx.stroke();
 		if(i<this.cnt_squares) {
			var txt = String(i+1);
			var w = this.ctx.measureText(txt).width/2;
			this.ctx.fillText(txt, x1-w-this.square_size/2, y+this.square_size/2);
			var txt = String.fromCharCode(97 + i).toUpperCase();
			var w = this.ctx.measureText(txt).width/2;
			this.ctx.fillText(txt, x-w+this.square_size/2, y1-this.square_size/2);
 		}
 	}
}

Game.prototype.render_ship = function (ship, fill_color, stroke_color, x_top_left, y_top_left, p) {
	y_top_left += this.square_size*2;

	var padding = 4;
	var f_point = 0.8;
		var x1 = x_top_left + ship.i*this.square_size + padding + 0.5;
		var y1 = y_top_left + ship.j*this.square_size + padding + 0.5;
	if(ship.is_vertical) {
 		var w = this.square_size - padding*2;
 		var h = ship.length*this.square_size - padding*2;
	} else {
 		var w = ship.length*this.square_size - padding*2;
 		var h = this.square_size - padding*2;
	}

	this.ctx.strokeStyle = stroke_color;
	this.ctx.lineWidth = 1.5;
	//this.ctx.strokeRect(x1, y1, w, h);

	if(fill_color!=null) this.ctx.fillStyle = fill_color;
	if(ship.is_vertical) {
 		this.ctx.beginPath();
     	this.ctx.moveTo(x1, y1+h);
 		this.ctx.lineTo(x1, y1+this.square_size*f_point);
		this.ctx.bezierCurveTo(x1, y1+this.square_size/6, x1+w/2, y1, x1+w/2, y1);
		this.ctx.bezierCurveTo(x1+w/2, y1, x1+w, y1+this.square_size/6, x1+w, y1+this.square_size*f_point, x1+w, y1+this.square_size*f_point);
 		this.ctx.lineTo(x1+w,y1+h);
 		this.ctx.closePath();
 		if(fill_color!=null) this.ctx.fill();
		this.ctx.stroke();
	} else {
		if(p==0) {
	 		this.ctx.beginPath();
	     	this.ctx.moveTo(x1,y1);
     		this.ctx.lineTo(x1+w-this.square_size*f_point, y1);
			this.ctx.bezierCurveTo(x1+w-this.square_size/6, y1, x1+w, y1+h/2, x1+w, y1+h/2);
			this.ctx.bezierCurveTo(x1+w, y1+h/2, x1+w-this.square_size/6, y1+h, x1+w-this.square_size*f_point, y1+h, x1+w-this.square_size*f_point, y1+w);
	 		this.ctx.lineTo(x1,y1+h);
	 		this.ctx.closePath();
	 		if(fill_color!=null) this.ctx.fill();
			this.ctx.stroke();
		} else {
	 		this.ctx.beginPath();
	     	this.ctx.moveTo(x1+w, y1);
     		this.ctx.lineTo(x1+this.square_size*f_point, y1);
			this.ctx.bezierCurveTo(x1+this.square_size/6, y1, x1, y1+h/2, x1, y1+h/2);
			this.ctx.bezierCurveTo(x1, y1+h/2, x1+this.square_size/6, y1+h, x1+this.square_size*f_point, y1+h, x1+this.square_size*f_point, y1+w);
	 		this.ctx.lineTo(x1+w,y1+h);
	 		this.ctx.closePath();
	 		if(fill_color!=null) this.ctx.fill();
			this.ctx.stroke();
		}
	}
}

Game.prototype.render_shot = function (shot, x_top_left, y_top_left) {
	y_top_left += this.square_size*2;
	if(shot.successfull) {
		var padding = 7;
 		var x = x_top_left + shot.i*this.square_size + padding + 0.5;
 		var y = y_top_left + shot.j*this.square_size + padding + 0.5;
 		var w = this.square_size - padding*2;
 		var h = this.square_size - padding*2;
		this.ctx.strokeStyle = 'red';
		this.ctx.lineWidth = 2;
 		this.ctx.beginPath();
 		this.ctx.moveTo(x+padding,y+padding);
 		this.ctx.lineTo(x+w-padding,y+w-padding);
 		this.ctx.stroke(); 			
 		this.ctx.beginPath();
 		this.ctx.moveTo(x+w-padding,y+padding);
 		this.ctx.lineTo(x+padding,y+w-padding);
 		this.ctx.stroke(); 			
	} else {
 		var x = x_top_left + (shot.i+0.5)*this.square_size;
 		var y = y_top_left + (shot.j+0.5)*this.square_size;
		this.ctx.fillStyle = 'blue';
		this.ctx.strokeStyle = 'blue';
		this.ctx.lineWidth = 1;
		this.ctx.beginPath();
		this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
		this.ctx.stroke();
		this.ctx.beginPath();
		this.ctx.arc(x, y, 8, 0, 2 * Math.PI);
		this.ctx.stroke();
	}
}

Game.prototype.render_target = function (shot, color, x_top_left, y_top_left) {
	y_top_left += this.square_size*2;
	var padding = 3;
	var x = x_top_left + shot.i*this.square_size + padding + 0.5;
	var y = y_top_left + shot.j*this.square_size + padding + 0.5;
	var w = this.square_size - padding*2;
	this.ctx.strokeStyle = color;
	this.ctx.lineWidth = 1.5;
	this.ctx.strokeRect(x, y, w, w)
}

Game.prototype.render = function () {

	this.ctx.fillStyle = 'white';
	this.ctx.fillRect(0,0,this.canvas_width,this.canvas_height);

	var txt = this.config.spectator ? 'Player 1' : 'My Ships';
	this.render_grid(txt, this.x_grid_left, this.y_grids);
	var txt = this.config.spectator ? 'Player 2' : 'Oponent\'s Ships';
	this.render_grid(txt, this.x_grid_right, this.y_grids);
	
	if(this.player_state==null) {
		return;
	}

	// winner
	this.ctx.fillStyle = 'red';
	this.ctx.textBaseline = 'top';
	this.ctx.font = 'bold 24px Arial';
	var y = this.y_grids + this.square_size*12.5;
	if(this.player_state.winner==0) {
		var txt = this.config.spectator ? 'Player 1 won!' : 'You won!';
		var w = this.ctx.measureText(txt).width/2;
		var x = this.x_grid_left + this.cnt_squares*this.square_size/2 - w;
		this.ctx.fillText(txt, x, y);
	}
	if(this.player_state.winner==1) {
		var txt = this.config.spectator ? 'Player 2 won!' : 'Oponent won!';
		var w = this.ctx.measureText(txt).width/2;
		var x = this.x_grid_right + this.cnt_squares*this.square_size/2 - w;
		this.ctx.fillText(txt, x, y);
	}

	if(this.player_state.selected_action!=null) {
		var action = this.player_state.selected_action;
		var fill_color = 'rgba(175,175,175,0.8)';
		var stroke_color = 'red';
		if(action.action_type == 'set_ship') {
			var x = this.player_state.idx_player_active==0 ? this.x_grid_left : this.x_grid_right;
			this.render_ship(action, fill_color, stroke_color, x, this.y_grids, this.player_state.idx_player_active);				
		}
		
	}

	var fill_color = 'rgb(200,200,200)';

 	for(var p=0; p<this.player_state.players.length; p++) {
		var player = this.player_state.players[p];
		var player2 = this.player_state.players[(p+1)%this.player_state.players.length];
		var x = p==0 ? this.x_grid_left : this.x_grid_right;
		
		// ships
		var stroke_color = 'black';
     	for(var i=0; i<player.ships.length; i++) {
			var ship = player.ships[i];
			if(ship.location!=null) {
				this.render_ship(ship, fill_color, stroke_color, x, this.y_grids, p);
			}
		}

		// shots
     	for(var i=0; i<player2.shots.length; i++) {
			var shot = player2.shots[i];
			this.render_shot(shot, x, this.y_grids);
		}
	}

	// selection ships
	if(this.player_state.phase == 'setup' && this.player_state.idx_player_active==this.player_state.idx_player_you && !this.config.spectator) {

		// text
		this.ctx.fillStyle = 'black';
		this.ctx.textBaseline = 'top';
		this.ctx.font = '20px Arial';
		var txt = 'Place your ships on the board.'
		var w = this.ctx.measureText(txt).width/2;
		var x = this.x_grid_left+this.cnt_squares*this.square_size/2-w;
		this.ctx.fillText(txt, x, this.y_grids+500);

		// shiptypes
     	for(var i=0; i<this.list_shiptypes.length; i++) {
			var shiptype = this.list_shiptypes[i];
			var fill_color = shiptype.is_selectable ? 'rgb(200,200,200)' : 'rgba(0,0,0,0.1)';
			if(shiptype.is_hidden) fill_color = null;
			var stroke_color = shiptype.is_selectable ? this.dict_colors[1] : 'rgba(0,0,0,0.1)';
			if(i==this.selection_state.i_shiptype_selected || i==this.selection_state.i_shiptype_hovered) {
				stroke_color = this.dict_colors[2];
			}
			this.render_ship(shiptype, fill_color, stroke_color, this.x_grid_left, this.y_grids, 0);
			/*
			this.ctx.strokeStyle = 'blue';
			this.ctx.strokeRect(shiptype.rect[0], shiptype.rect[1], shiptype.rect[2], shiptype.rect[3]);
			*/
		}


		// actions
		if(this.selection_state.i_shiptype_selected!=null) {
			var fill_color = null;
			var stroke_color = this.dict_colors[1];
			for(var i=0; i<this.player_state.list_action.length; i++) {
				var action = this.player_state.list_action[i];
				if(action.is_selectable && this.selection_state.i_ship_hovered!=i && this.selection_state.i_ship_selected!=i) {
					this.render_ship(action, fill_color, stroke_color, this.x_grid_left, this.y_grids, 0);				
				}
			}
			var stroke_color = this.dict_colors[2];
			for(var i=0; i<this.player_state.list_action.length; i++) {
				var action = this.player_state.list_action[i];
				if(this.selection_state.i_ship_hovered==i || this.selection_state.i_ship_selected==i) {
					this.render_ship(action, fill_color, stroke_color, this.x_grid_left, this.y_grids, 0);				
				}
			}
		}

	} else if(this.player_state.phase == 'running') {

		if(!this.config.spectator) {
			// text
			this.ctx.fillStyle = 'black';
			this.ctx.textBaseline = 'top';
			this.ctx.font = '20px Arial';
			var txt = 'Shoot oponents ships.'
			var w = this.ctx.measureText(txt).width/2;
			var x = this.x_grid_right+this.cnt_squares*this.square_size/2-w;
			this.ctx.fillText(txt, x, this.y_grids+500);
		}

		// actions
		for(var i=0; i<this.player_state.list_action.length; i++) {
			var action = this.player_state.list_action[i];
			color = i==this.selection_state.i_target_hovered || i==this.selection_state.i_target_selected ? this.dict_colors[2] : this.dict_colors[1];
			this.render_target(action, color, this.x_grid_right, this.y_grids);
		}

	}


	// submit button
	if(this.selection_state.submit_button_state!=null) {
		// game state
		var button = this.dict_area_rect[this.ID_BUTTON_SUBMIT];
		var rect = button.rect;
		this.ctx.font = button.f+'px Arial';
		this.ctx.fillStyle = 'rgba(0,0,0,0.2)';
		this.ctx.fillRect(rect[0]+5, rect[1]+10, rect[2], rect[3]);

		this.ctx.fillStyle = 'white';
		this.ctx.strokeStyle = this.dict_colors[this.selection_state.submit_button_state];
		this.ctx.fillRect(rect[0], rect[1], rect[2], rect[3]);
		this.ctx.strokeRect(rect[0], rect[1], rect[2], rect[3]);
		this.ctx.fillStyle = 'black';
		this.ctx.textBaseline = 'top';
		this.ctx.textAlign = 'left';
		this.ctx.fillText(button.txt, rect[0]+button.dx, rect[1]+button.dy);
	}

}
