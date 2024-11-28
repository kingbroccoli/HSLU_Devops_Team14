function Game(config) {
	this.config = config;
	this.canvas_width = 1000;
	this.canvas_height = 1000;
	this.r_card_border = 12;
	this.r_card_colors = 14;
	this.w_callout = 480/5;
	this.h_callout = 451/5;

	this.list_assets = [
		{'id':'red_0', 'src': 'cards/red_0.png'},
		{'id':'red_1', 'src': 'cards/red_1.png'},
		{'id':'red_2', 'src': 'cards/red_2.png'},
		{'id':'red_3', 'src': 'cards/red_3.png'},
		{'id':'red_4', 'src': 'cards/red_4.png'},
		{'id':'red_5', 'src': 'cards/red_5.png'},
		{'id':'red_6', 'src': 'cards/red_6.png'},
		{'id':'red_7', 'src': 'cards/red_7.png'},
		{'id':'red_8', 'src': 'cards/red_8.png'},
		{'id':'red_9', 'src': 'cards/red_9.png'},
		{'id':'red_draw2', 'src': 'cards/red_draw.png'},
		{'id':'red_reverse', 'src': 'cards/red_reverse.png'},
		{'id':'red_skip', 'src': 'cards/red_skip.png'},
		{'id':'blue_0', 'src': 'cards/blue_0.png'},
		{'id':'blue_1', 'src': 'cards/blue_1.png'},
		{'id':'blue_2', 'src': 'cards/blue_2.png'},
		{'id':'blue_3', 'src': 'cards/blue_3.png'},
		{'id':'blue_4', 'src': 'cards/blue_4.png'},
		{'id':'blue_5', 'src': 'cards/blue_5.png'},
		{'id':'blue_6', 'src': 'cards/blue_6.png'},
		{'id':'blue_7', 'src': 'cards/blue_7.png'},
		{'id':'blue_8', 'src': 'cards/blue_8.png'},
		{'id':'blue_9', 'src': 'cards/blue_9.png'},
		{'id':'blue_draw2', 'src': 'cards/blue_draw.png'},
		{'id':'blue_reverse', 'src': 'cards/blue_reverse.png'},
		{'id':'blue_skip', 'src': 'cards/blue_skip.png'},
		{'id':'green_0', 'src': 'cards/green_0.png'},
		{'id':'green_1', 'src': 'cards/green_1.png'},
		{'id':'green_2', 'src': 'cards/green_2.png'},
		{'id':'green_3', 'src': 'cards/green_3.png'},
		{'id':'green_4', 'src': 'cards/green_4.png'},
		{'id':'green_5', 'src': 'cards/green_5.png'},
		{'id':'green_6', 'src': 'cards/green_6.png'},
		{'id':'green_7', 'src': 'cards/green_7.png'},
		{'id':'green_8', 'src': 'cards/green_8.png'},
		{'id':'green_9', 'src': 'cards/green_9.png'},
		{'id':'green_draw2', 'src': 'cards/green_draw.png'},
		{'id':'green_reverse', 'src': 'cards/green_reverse.png'},
		{'id':'green_skip', 'src': 'cards/green_skip.png'},
		{'id':'yellow_0', 'src': 'cards/yellow_0.png'},
		{'id':'yellow_1', 'src': 'cards/yellow_1.png'},
		{'id':'yellow_2', 'src': 'cards/yellow_2.png'},
		{'id':'yellow_3', 'src': 'cards/yellow_3.png'},
		{'id':'yellow_4', 'src': 'cards/yellow_4.png'},
		{'id':'yellow_5', 'src': 'cards/yellow_5.png'},
		{'id':'yellow_6', 'src': 'cards/yellow_6.png'},
		{'id':'yellow_7', 'src': 'cards/yellow_7.png'},
		{'id':'yellow_8', 'src': 'cards/yellow_8.png'},
		{'id':'yellow_9', 'src': 'cards/yellow_9.png'},
		{'id':'yellow_draw2', 'src': 'cards/yellow_draw.png'},
		{'id':'yellow_reverse', 'src': 'cards/yellow_reverse.png'},
		{'id':'yellow_skip', 'src': 'cards/yellow_skip.png'},
		{'id':'_wild', 'src': 'cards/wild.png'},
		{'id':'_wilddraw4', 'src': 'cards/wild_draw.png'},
		{'id':'back', 'src': 'cards/deck.png'},
	]
	this.path_direction = new Path2D("M456.213,730.502c-34.613,0-68.516-5.831-100.765-17.331c-31.171-11.115-60.159-27.272-86.161-48.024 c-52.042-41.536-89.225-99.817-104.693-164.109c-6.783-28.189-35.133-45.546-63.325-38.761 c-28.19,6.783-45.544,35.135-38.761,63.325c10.557,43.872,28.304,85.42,52.748,123.492c23.995,37.372,53.782,70.384,88.534,98.118 c35.098,28.013,74.258,49.833,116.393,64.858c43.6,15.547,89.367,23.431,136.031,23.431c54.643,0,107.678-10.713,157.633-31.843 c48.225-20.396,91.523-49.587,128.695-86.758s66.361-80.471,86.76-128.696c21.129-49.956,31.842-102.99,31.842-157.633 c0-54.642-10.713-107.678-31.842-157.633c-20.398-48.225-49.588-91.525-86.76-128.696S662.07,77.881,613.846,57.484 c-49.955-21.13-102.99-31.843-157.633-31.843c-79.907,0-157.211,23.258-223.558,67.259c-52.833,35.04-96.38,81.557-127.655,135.996 v-84.329c0-28.995-23.505-52.5-52.5-52.5S0,115.572,0,144.567v198.884c0,28.995,23.505,52.5,52.5,52.5h196.21 c28.994,0,52.5-23.505,52.5-52.5c0-28.995-23.506-52.5-52.5-52.5h-58.027c23.445-44.539,57.708-82.493,100.006-110.546 c49.088-32.555,106.324-49.763,165.522-49.763c80.113,0,155.434,31.198,212.084,87.848c56.648,56.65,87.848,131.967,87.848,212.081 s-31.197,155.434-87.848,212.083S536.326,730.502,456.213,730.502z");
	this.path_callout = new Path2D("m71.183 5.0014 336.96 2.398c20.82 0.148 56.06 5.474 63.56 34.775 8.66 38.53 11.55 211.95-2.4 238.63-10.28 21.52-19.83 28.7-29.98 34.78-30.06 14.44-170.28 11.99-170.28 11.99l-178.67 100.73 115.12-101.93h-145.1c-20.357 0-38.976-12.81-45.564-40.77-11.469-50.79-13.702-193.22-2.396-226.64 10.714-30.536 28.721-54.173 58.758-53.959z");
	this.dict_colors = {
		1: 'rgb(0,220,0)',
		2: 'magenta',
		3: 'black',
	}
	this.dict_card_colors = {
		'red': 'rgb(234,50,60)',
		'green': 'rgb(51,152,75)',
		'blue': 'rgb(0,152,220)',
		'yellow': 'rgb(255,200,37)',
	}
	this.ID_AREA_DRAW = 'draw';
	this.ID_AREA_DISCARD = 'discard';
	this.dict_area_rect = null;
	this.list_card_selectable = null;
	this.list_ball_selectable_from = null;
	this.list_ball_selectable_to = null;
	this.dict_imgs = null;
	this.state = null;
	this.selection_state = null;
	this.imgs_loaded = false;
	this.idx_player_you = 0;

	this.init();
}

Game.prototype.init = function () {
	this.canvas = document.getElementById(this.config.canvas_id);
	this.ctx = this.canvas.getContext("2d");
	this.canvas.width = this.canvas_width;
	this.canvas.height = this.canvas_height;
	this.load_images();
	this.bind_events();
}

Game.prototype.load_images = function () {
	this.dict_imgs = {}
	this.imgs_loaded = false;
	this.cnt_images_loaded = 0;

	for(var i=0; i<this.list_assets.length; i++) {
		var asset = this.list_assets[i];
		var img = new Image();
		img.src = this.config.img_path + asset['src'];
		img.onload = function() {
	      	this.cnt_images_loaded++;
			if(this.cnt_images_loaded==this.list_assets.length) {
				this.imgs_loaded = true;
				this.calc_objects_rect();
				this.render();
			}
	    }.bind(this);
		this.dict_imgs[asset['id']] = img;
	}
}

Game.prototype.bind_events = function() {
	this.canvas.onmousemove = this.on_mouse_move.bind(this);
	this.canvas.onmousedown = this.on_mouse_down.bind(this);
}

Game.prototype.set_state = function(state) {
	this.selection_state = {
		'idx_card_hover': null,
		'idx_card_selected': null,
		'idx_color_hover': null,
		'idx_color_selected': null,
		'callout_hover': null,
		'callout_selected': null,
	};
	this.list_card_selectable = [];
	this.list_ball_selectable_from = [];
	this.list_ball_selectable_to = [];
	this.state = this.transform_state(state);
	
	this.calc_objects_rect();
	//console.log(this.state)
	this.render();
}

Game.prototype.get_id_from_card = function(card) {
	var id = card.color + '_' + card.number;
	if(card.color=='any') {
		id = '_'+card.symbol;
	} else {
		if(card.symbol!=null) {
			if(card.color==null) {
				id = card.symbol;
			} else {
				id = card.color + '_' + card.symbol;
			}
		}
	}
	return id;
}

Game.prototype.transform_state = function(state) {
	// set card.id
	for(var p=0; p<state.list_player.length; p++) {
		var player = state.list_player[p];
		for(var i=0; i<player.list_card.length; i++) {
			var card = player.list_card[i];
			card.id = this.get_id_from_card(card);
		}
	}
	for(var i=0; i<state.list_card_discard.length; i++) {
		var card = state.list_card_discard[i];
		card.id = this.get_id_from_card(card);
	}
	for(var i=0; i<state.list_card_draw.length; i++) {
		var card = state.list_card_draw[i];
		card.id = this.get_id_from_card(card);
	}
	for(var i=0; i<state.list_action.length; i++) {
		var action = state.list_action[i];
		if(action.card==null) continue;
		action.card.id = this.get_id_from_card(action.card);
	}

	// sort players cards
	function sortCards(a,b) {
		if ( a.id < b.id ){
			return -1;
		}
		if ( a.id > b.id ){
			return 1;
		}
		return 0;
	}
	for(var p=0; p<state.list_player.length; p++) {
		var player = state.list_player[p];
		player.list_card.sort(sortCards);
	}

	return state;
}


Game.prototype.calc_objects_rect = function() {

	this.dict_area_rect = {};

	var x_center = this.canvas_width / 2;
	var y_center = this.canvas_height / 2;
	var r = x_center*0.95;
	var r_txt_cnt_cards = x_center*0.88;
	var r_txt_name = x_center*0.95;
	var r_txt_winner = x_center*0.61;
	var r2 = 160;
	var f = 0.33;
	var w = 388*f;
	var h = 562*f;

	var p = 5;
	var y = y_center - h/2;

	// cards center: draw, discard
	for(var i=0; i<2; i++) {
		var area_id = i==0 ? this.ID_AREA_DRAW : this.ID_AREA_DISCARD;
		var x = i==0 ? x_center-w-p : x_center+p;
		var card_id = i==0 ? 'back' : this.state.list_card_discard[this.state.list_card_discard.length-1].id;

		var rect = [
			[x, y],
			[x+w, y],
			[x+w, y+h],
			[x, y+h],
		];
		var border = [
			[x+w-this.r_card_border, y],
			[x+w-this.r_card_border, y+this.r_card_border],
			[x+w,          y+h-this.r_card_border],
			[x+w-this.r_card_border, y+h-this.r_card_border],
			[x+this.r_card_border, y+h],
			[x+this.r_card_border, y+h-this.r_card_border],
			[x,          y+this.r_card_border],
			[x+this.r_card_border, y+this.r_card_border]
		];
		this.dict_area_rect[area_id] = {
			'x': x,
			'y': y,
			'w': w,
			'h': h,
			'id': card_id,
			'rect': rect,
			'border': border,
		};

		if(this.state==null) {
			return
		}
	}

	this.calc_selectable();

	var alpha_delta = Math.PI*2/this.state.cnt_player;

	// players cards
	for(var i=0; i<this.state.cnt_player; i++) {

		var alpha = alpha_delta*i + Math.PI/2;
		var x = x_center - Math.cos(alpha)*r;
		var y = y_center + Math.sin(alpha)*r;

		var player = this.state.list_player[i];
		player.x_txt_cnt_cards = x_center - Math.cos(alpha)*r_txt_cnt_cards;
		player.y_txt_cnt_cards = y_center + Math.sin(alpha)*r_txt_cnt_cards;
		player.x_txt_name = x_center - Math.cos(alpha)*r_txt_name;
		player.y_txt_name = y_center + Math.sin(alpha)*r_txt_name;
		player.x_txt_winner = x_center - Math.cos(alpha)*r_txt_winner;
		player.y_txt_winner = y_center + Math.sin(alpha)*r_txt_winner;
		player.x_callout = player.x_txt_winner+Math.cos(-alpha+Math.PI/2)*120+Math.cos(-alpha)*50;
		player.y_callout = player.y_txt_winner+Math.sin(-alpha+Math.PI/2)*120+Math.sin(-alpha)*50;
		player.alpha_callout = -alpha+Math.PI/2;
		player.x_callout_text = 5*this.w_callout/4;
		player.y_callout_text = 5*this.h_callout/2.25;
		if(i==this.state.idx_player_you) {
			player.rect_callout = [
				[player.x_callout, player.y_callout],
				[player.x_callout+this.w_callout, player.y_callout],
				[player.x_callout+this.w_callout, player.y_callout+this.h_callout],
				[player.x_callout, player.y_callout+this.h_callout],
			];
		}

		var alpha_delta2 = Math.min(Math.PI*0.6/(player.list_card.length-1), Math.PI/0.6/20);

		for(var j=player.list_card.length-1; j>=0; j--) {
			var card = player.list_card[j];
			var alpha2 = alpha + Math.PI + (j-(player.list_card.length-1)/2)*alpha_delta2;
			if(player.list_card.length==1) {
				alpha2 = alpha + Math.PI
			}
			if(card.is_selectable) {
				card.x_center = x-Math.cos(alpha2)*r2*1.2;
				card.y_center = y+Math.sin(alpha2)*r2*1.2;				

			} else {
				card.x_center = x-Math.cos(alpha2)*r2;
				card.y_center = y+Math.sin(alpha2)*r2;				
			}

			var v1_x = -Math.cos(alpha2+Math.PI/2)*w/2;
			var v1_y = Math.sin(alpha2+Math.PI/2)*w/2;
			var v2_x = -Math.cos(alpha2)*h/2;
			var v2_y = Math.sin(alpha2)*h/2;
			card.rect = [
				[card.x_center-v1_x-v2_x, card.y_center-v1_y-v2_y],
				[card.x_center+v1_x-v2_x, card.y_center+v1_y-v2_y],
				[card.x_center+v1_x+v2_x, card.y_center+v1_y+v2_y],
				[card.x_center-v1_x+v2_x, card.y_center-v1_y+v2_y],
			];
			card.alpha = -alpha2+Math.PI/2;
			card.x = -w/2;
			card.y = -h/2;
			card.w = w;
			card.h = h;
			card.border = [
				[ w/2-this.r_card_border, -h/2],
				[ w/2-this.r_card_border, -h/2+this.r_card_border],
				[ w/2,    h/2-this.r_card_border],
				[ w/2-this.r_card_border,  h/2-this.r_card_border],
				[-w/2+this.r_card_border,  h/2],
				[-w/2+this.r_card_border,  h/2-this.r_card_border],
				[-w/2,   -h/2+this.r_card_border],
				[-w/2+this.r_card_border, -h/2+this.r_card_border]
			];
			if(i==this.state.idx_player_you) {
				card.bbox = {
					'x_min': null,
					'x_max': null,
					'y_min': null,
					'y_max': null,
				};
				for(var k=0; k<4; k++) {
					if(card.bbox.x_min==null || card.bbox.x_min>card.rect[k][0]) {
						card.bbox.x_min = card.rect[k][0];
					}
					if(card.bbox.x_max==null || card.bbox.x_max<card.rect[k][0]) {
						card.bbox.x_max = card.rect[k][0];
					}
					if(card.bbox.y_min==null || card.bbox.y_min>card.rect[k][1]) {
						card.bbox.y_min = card.rect[k][1];
					}
					if(card.bbox.y_max==null || card.bbox.y_max<card.rect[k][1]) {
						card.bbox.y_max = card.rect[k][1];
					}
				}

				if(card.color=='any') {
					card.pos_colors = [];
					for(var k=0; k<4; k++) {
						var x_color = card.rect[2][0] + (k+0.5)*(card.rect[3][0]-card.rect[2][0]) / 4;
						var y_color = card.rect[2][1] + (k+0.5)*(card.rect[3][1]-card.rect[2][1]) / 4;
						x_color += (card.rect[2][0]-card.rect[1][0])/8;
						y_color += (card.rect[2][1]-card.rect[1][1])/8;
						card.pos_colors.push([x_color,y_color]);
					}
				}
			}
		}
	}

}

Game.prototype.calc_selectable = function() {
 	if(this.config.spectator || this.state.idx_player_active!=this.state.idx_player_you) {
 		return;
 	}

 	var player = this.state.list_player[this.idx_player_you];

 	// cards
 	this.dict_area_rect[this.ID_AREA_DRAW].is_selectable = false;
 	player.cnt_hand_cards_selectable = 0;
 	for(var j=0; j<player.list_card.length; j++) {
 		var card = player.list_card[j];
 		card.is_selectable = false;

		for(var i=0; i<this.state.list_action.length; i++) {
			var action = this.state.list_action[i];
			if(action.card==null) {
				this.dict_area_rect[this.ID_AREA_DRAW].is_selectable = true;
				this.dict_area_rect[this.ID_AREA_DRAW].action = action;
				this.dict_area_rect[this.ID_AREA_DRAW].action.uno = false;
				continue;
			}

     		if(action.card.id==card.id) {
				card.is_selectable = true;
				card.action = action;
				card.action.uno = false;
				player.cnt_hand_cards_selectable++;
     			break;
     		}
     	}
	}

	if(player.list_card.length==2 && player.cnt_hand_cards_selectable>0) {
		this.selection_state.callout_hover = false;
	} else {
		this.selection_state.callout_hover = null;
	}

}


Game.prototype.on_mouse_move = function(e) {
 	if(this.can_select()) return;

 	var xy = this.get_xy_from_cursor(e);
 	var do_render = false;


 	var player = this.state.list_player[this.idx_player_you];

 	// check cards
 	var idx_card_before = this.selection_state.idx_card_hover;
 	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_AREA_DRAW].rect)) {
     	this.selection_state.idx_card_hover = -1; // draw
 	} else {
 		this.selection_state.idx_card_hover = null;
 	}
 	for(var j=0; j<player.list_card.length; j++) {
 		var card = player.list_card[j];
 		if(card.is_selectable && this.is_point_in_rotated_rect(xy, card.bbox, card.rect)) {
	     	this.selection_state.idx_card_hover = j;
	     	break;
 		}
 	}
 	do_render |= idx_card_before!=this.selection_state.idx_card_hover;

 	// check colors
 	if(this.selection_state.idx_card_selected!=null && this.selection_state.idx_card_selected>=0) {
 		var card = player.list_card[this.selection_state.idx_card_selected];
 		if(card.color=='any') {
		 	var idx_color_before = this.selection_state.idx_color_hover;
		 	this.selection_state.idx_color_hover = null;
		 	for(var j=0; j<4; j++) {
			 	if(this.is_point_in_circle(xy, card.pos_colors[j], this.r_card_colors)) {
			     	this.selection_state.idx_color_hover = j;
			 	}
			}
			do_render |= idx_color_before!=this.selection_state.idx_color_hover;
		}
 	}

 	// check callout
 	if(this.selection_state.callout_hover!=null) {
 		var callout_hover_before = this.selection_state.callout_hover;
 		this.selection_state.callout_hover = this.is_point_in_rect(xy, player.rect_callout);
 		do_render |= callout_hover_before!=this.selection_state.callout_hover;
 	}

 	if(do_render) {
 		this.render();
 	}
}

Game.prototype.on_mouse_down = function(e) {
 	if(this.can_select()) return;

 	var xy = this.get_xy_from_cursor(e);
 	var player = this.state.list_player[this.idx_player_you];

 	// check callout
 	if(this.selection_state.callout_hover!=null && this.is_point_in_rect(xy, player.rect_callout)) {
 		this.selection_state.callout_selected = true;
	 	for(var j=0; j<player.list_card.length; j++) {
	 		var card = player.list_card[j];
	 		if(card.is_selectable) {
		 		card.action.uno = true;
	 		}
	 	}
 	}

 	// check card color
 	if(this.selection_state.idx_card_selected!=null && this.selection_state.idx_card_selected>=0) {
 		var card = player.list_card[this.selection_state.idx_card_selected];
 		if(card.color=='any') {
		 	for(var j=0; j<4; j++) {
			 	if(this.is_point_in_circle(xy, card.pos_colors[j], this.r_card_colors)) {
			 		card.action.color = Object.keys(this.dict_card_colors)[j];
		 			this.send_action_callback(card.action);
		 			break;
			 	}
			}
 		}
 	}

 	// check draw card
 	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_AREA_DRAW].rect)) {
     	this.selection_state.idx_card_selected = -1; // draw
 	} else {
 		this.selection_state.idx_card_selected = null;
 	}

 	// check player cards
 	for(var j=0; j<player.list_card.length; j++) {
 		var card = player.list_card[j];
 		if(card.is_selectable && this.is_point_in_rotated_rect(xy, card.bbox, card.rect)) {
	     	this.selection_state.idx_card_selected = j;
	     	break;
 		}
 	}

 	if(this.selection_state.idx_card_selected!=null) {
 		if(this.selection_state.idx_card_selected==-1) {
 			this.send_action_callback(this.dict_area_rect[this.ID_AREA_DRAW].action);
 		} else {
	 		var card = player.list_card[this.selection_state.idx_card_selected];
	 		if(card.color!='any') {
	 			this.send_action_callback(card.action);
	 		}
 		}
 	}

 	this.render();
}

Game.prototype.send_action_callback = function(action) {	
}

Game.prototype.can_select = function(e) {
 	return this.state==null || this.selection_state==null || this.state.idx_player_active!=this.state.idx_player_you;
}

Game.prototype.get_xy_from_cursor = function(e) {
 	var x = e.offsetX || (e.pageX - this.canvas.offsetLeft);
 	var y = e.offsetY || (e.pageY - this.canvas.offsetTop);
 	return [x, y];
}

Game.prototype.is_point_in_rect = function(xy, rect) {
	return xy[0]>rect[0][0] && xy[0]<rect[2][0] && xy[1]>rect[0][1] && xy[1]<rect[2][1];
}

Game.prototype.is_point_in_rotated_rect = function(xy, bbox, poly) {
	if(xy[0]>bbox.x_min && xy[0]<bbox.x_max && xy[1]>bbox.y_min && xy[1]<bbox.y_max) {
		return this.is_point_in_poly(xy, poly)
	}
	return false;
}

Game.prototype.is_point_in_poly = function(xy, poly) {
    // ray-casting algorithm based on
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
    var x = xy[0], y = xy[1];
    var inside = false;
    for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
        var xi = poly[i][0], yi = poly[i][1];
        var xj = poly[j][0], yj = poly[j][1];
        var intersect = ((yi > y) != (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
};

Game.prototype.is_point_in_circle = function(xy, xy_center, r) {
	return (xy[0]-xy_center[0])**2 + (xy[1]-xy_center[1])**2 < r**2;
}

Game.prototype.render_card_area = function (card) {
	this.ctx.strokeStyle = 'blue';
	this.ctx.lineWidth = 1;
	this.ctx.beginPath();
	this.ctx.moveTo(card.rect[0][0], card.rect[0][1]);
	this.ctx.lineTo(card.rect[1][0], card.rect[1][1]);
	this.ctx.lineTo(card.rect[2][0], card.rect[2][1]);
	this.ctx.lineTo(card.rect[3][0], card.rect[3][1]);
	this.ctx.closePath();
	this.ctx.stroke();
}

Game.prototype.render_card = function (card, idx_card) {
	this.ctx.drawImage(this.dict_imgs[card.id], card.x, card.y, card.w, card.h);

	if(card.is_selectable) {
		var color = this.dict_colors[1];
		if(this.selection_state.idx_card_hover==idx_card || this.selection_state.idx_card_selected==idx_card) {
			color = this.dict_colors[2];
		}
		this.ctx.strokeStyle = color;
		this.ctx.lineWidth = 2;
	} else {
		this.ctx.strokeStyle = 'grey';
		this.ctx.lineWidth = 1;
	}

	this.ctx.beginPath();
	this.ctx.moveTo(card.border[0][0], card.border[0][1]);
	this.ctx.arc(   card.border[1][0], card.border[1][1], this.r_card_border, -Math.PI/2, 0);
	this.ctx.lineTo(card.border[2][0], card.border[2][1]);
	this.ctx.arc(   card.border[3][0], card.border[3][1], this.r_card_border, 0, Math.PI/2);
	this.ctx.lineTo(card.border[4][0], card.border[4][1]);
	this.ctx.arc(   card.border[5][0], card.border[5][1], this.r_card_border, Math.PI/2, Math.PI);
	this.ctx.lineTo(card.border[6][0], card.border[6][1]);
	this.ctx.arc(   card.border[7][0], card.border[7][1], this.r_card_border, Math.PI, -Math.PI/2);
	this.ctx.closePath();
	this.ctx.stroke();

}

Game.prototype.render_card_colors = function (card) {
	for(var i=0; i<4; i++) {
		var color = Object.keys(this.dict_card_colors);
		this.ctx.fillStyle = this.dict_card_colors[color[i]];
		color = this.dict_colors[1];
		if(this.selection_state.idx_color_hover==i) {
			color = this.dict_colors[2];
		}
		this.ctx.strokeStyle = color;
		this.ctx.lineWidth = 2;
		this.ctx.beginPath();
		var x = card.pos_colors[i][0];
		var y = card.pos_colors[i][1];
		this.ctx.arc(x, y, this.r_card_colors, 0, Math.PI*2);
		this.ctx.fill();
		this.ctx.stroke();
	}
}						

Game.prototype.render_shadow = function (card) {

	this.ctx.fillStyle = 'rgba(0,0,0,0.2)';
	this.ctx.beginPath();
	var x = card.border[1][0]+this.r_card_border;
	var y = card.border[1][1]-this.r_card_border/2;
	var x2 = card.border[5][0]-this.r_card_border;
	var y2 = card.border[5][1]+this.r_card_border/2;
	var d = 30;
	this.ctx.moveTo(x, y);
	this.ctx.arc(   x-this.r_card_border+d, y+this.r_card_border/2+d, this.r_card_border, -Math.PI/4, 0);
	this.ctx.arc(   card.border[3][0]+d, card.border[3][1]+d, this.r_card_border, 0, Math.PI/2);
	this.ctx.lineTo(card.border[4][0]+d, card.border[4][1]+d);
	this.ctx.arc(   card.border[5][0]+d, card.border[5][1]+d, this.r_card_border, Math.PI/2, Math.PI/4*3);
	this.ctx.lineTo(x2, y2);
	this.ctx.closePath();
	this.ctx.fill();
}

Game.prototype.render = function () {
	if(!this.imgs_loaded ) {
		return;
	}
	if(this.state==null){
		this.ctx.fillStyle = 'white';
		this.ctx.fillRect(0,0,this.canvas_width,this.canvas_height);

		var card = this.dict_area_rect[this.ID_AREA_DRAW];
		this.render_shadow(card);
		this.render_card(card, -1);

		return;
	}

	this.ctx.fillStyle = 'white';
	this.ctx.fillRect(0,0,this.canvas_width,this.canvas_height);

	var card = this.dict_area_rect[this.ID_AREA_DISCARD];
	this.render_card(card);
	//this.render_card_area(card);

	// color for WILD cards
	if(this.state.list_card_discard[this.state.list_card_discard.length-1].color=='any' || this.state.cnt_to_draw>0) {
		this.ctx.fillStyle = this.dict_card_colors[this.state.color];
		this.ctx.strokeStyle = 'black';
		this.ctx.lineWidth = 1;
		this.ctx.beginPath();
		var x = card.border[0][0]+this.r_card_border/2;
		var y = card.border[0][1]+this.r_card_border/2;
		this.ctx.arc(x, y, 20, 0, Math.PI*2);
		this.ctx.fill();
		this.ctx.stroke();

		if(this.state.cnt_to_draw>0) {
			this.ctx.font = 'bold 20px Arial';
			this.ctx.fillStyle = 'white';
			var txt = '+'+this.state.cnt_to_draw;
			var w = this.ctx.measureText(txt).width;
			this.ctx.fillText(txt, x-w/2, y+8);
		}
	}

	var card = this.dict_area_rect[this.ID_AREA_DRAW];
	this.render_shadow(card);
	this.render_card(card, -1);
	//this.render_card_area(card);

	this.ctx.save();
	this.ctx.translate(this.canvas_width/2+this.state.direction*-23, this.canvas_height/2+110);
	this.ctx.scale(this.state.direction*0.05, 0.05);
	this.ctx.fillStyle = 'grey';
	this.ctx.fill(this.path_direction);
	this.ctx.restore();

	for(var i=0; i<this.state.cnt_player; i++) {

		var player = this.state.list_player[i];
		for(var j=player.list_card.length-1; j>=0; j--) {
			var card = player.list_card[j];
			if(i==this.state.idx_player_you) {
		 		if(this.selection_state.idx_card_selected==j && card.color=='any') {
		 			this.render_card_colors(card);
				}
				if(this.selection_state.idx_card_hover==j) {
					continue;
				}
			}
			this.ctx.save();
			this.ctx.translate(card.x_center, card.y_center);
			this.ctx.rotate(card.alpha+Math.PI);
			this.render_card(card, j);
			this.ctx.restore();
			//this.render_card_area(card);
		}

		if(i==this.state.idx_player_you && this.selection_state.idx_card_hover!=null) {
			for(var j=player.list_card.length-1; j>=0; j--) {
				var card = player.list_card[j];
				if(this.selection_state.idx_card_hover!=j) {
					continue;
				}
				this.ctx.save();
				this.ctx.translate(card.x_center, card.y_center);
				this.ctx.rotate(card.alpha+Math.PI);
				this.render_card(card, j);
				this.ctx.restore();
				//this.render_card_area(card);
			}
		}

		// cnt cards
		this.ctx.textAlign = 'middle';
		if(player.list_card.length>0) {
			this.ctx.font = '20px Arial';
			this.ctx.fillStyle = 'black';
			var txt = player.list_card.length;
			var w = this.ctx.measureText(txt).width;
			var x = player.x_txt_cnt_cards - w/2;
			var y = player.y_txt_cnt_cards;
		} else {
			this.ctx.font = 'bold 20px Arial';
			this.ctx.fillStyle = 'red';
			var txt = 'WINNER!';
			var w = this.ctx.measureText(txt).width;
			var x = player.x_txt_winner - w/2;
			var y = player.y_txt_winner;
		}
		this.ctx.fillText(txt, x, y);

		// player names
		if(this.state['list_player_names']!=undefined) {
			this.ctx.font = '24px Arial';
			this.ctx.textBaseline = 'middle';
			var txt = this.state['list_player_names'][i];
			var w = this.ctx.measureText(txt).width/2;
			var x = player.x_txt_name;
			var y = player.y_txt_name;
			var a = i%2*+Math.PI/2;
			this.ctx.fillStyle = 'black';
			this.ctx.save();
			this.ctx.translate(x, y);
			this.ctx.rotate(a);
			this.ctx.fillText(txt, -w, 0);
			this.ctx.restore();
		}

		if(player.list_card.length==2) {
			var show = this.config.spectator;
			show |= i==this.state.idx_player_active && i==this.state.idx_player_you && player.cnt_hand_cards_selectable>0;
			if(show) {
				var color = 'grey';
				if(!this.config.spectator && i==this.state.idx_player_active && i==this.state.idx_player_you) {
					color = this.selection_state.callout_hover || this.selection_state.callout_selected ? this.dict_colors[2] : this.dict_colors[1];
				}
				this.ctx.save();
				this.ctx.translate(player.x_callout, player.y_callout);
				this.ctx.rotate(player.alpha_callout);
				this.ctx.lineWidth = 10;
				this.ctx.scale(0.2, 0.2);
				this.ctx.strokeStyle = color;
				this.ctx.stroke(this.path_callout);
				this.ctx.font = 'bold 100px Arial';
				this.ctx.fillText('UNO!', player.x_callout_text, player.y_callout_text);
				this.ctx.restore();
			}
		}

		/*
		// callout area
		if(i==this.state.idx_player_you) {
			this.ctx.strokeStyle = 'blue';
			this.ctx.lineWidth = 1;
			this.ctx.beginPath();
			this.ctx.moveTo(player.rect_callout[0][0], player.rect_callout[0][1]);
			this.ctx.lineTo(player.rect_callout[1][0], player.rect_callout[1][1]);
			this.ctx.lineTo(player.rect_callout[2][0], player.rect_callout[2][1]);
			this.ctx.lineTo(player.rect_callout[3][0], player.rect_callout[3][1]);
			this.ctx.closePath();
			this.ctx.stroke();
		}
		*/

	}
 


}



