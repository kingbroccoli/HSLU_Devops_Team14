function Singleplayer(config) {
    this.config = config
    this.game = new Game(config.game_config);
    this.game.send_action_callback = this.send_action.bind(this);
    this.ws = null;
    this.main();
};
Singleplayer.prototype.main = function(){
    this.init_websocket();
};
Singleplayer.prototype.init_websocket = function(){
    this.ws = new WebSocket(this.config.ws_endpoint);
    this.ws.onopen = this.ws_onopen.bind(this);
    this.ws.onmessage = this.ws_onmessage.bind(this);
}
Singleplayer.prototype.ws_onopen = function(event) {
    this.add_log('> connected');
};
Singleplayer.prototype.ws_send = function(data) {
    this.add_log('< '+data['type']);
    this.ws.send(JSON.stringify(data))
};
Singleplayer.prototype.ws_onmessage = function(event) {
    var data = JSON.parse(event.data);
    this.add_log('> '+data.type);
    switch(data['type']) {
        case 'update':
    		this.game.set_player_state(data['state']);
    		//console.log(data['state']);
    		/*if(data['state']['idx_player_active']==data['state']['idx_player_you'] && data['state']['list_action'].length==0) {
    			this.send_action(null);
    		}*/
    		//this.apply_action(data['state']['selected_action']);
            break;
    }
};
Singleplayer.prototype.add_log = function(msg) {
    //console.log(msg);
};

Singleplayer.prototype.apply_action = function(action) {
	if(this.game.player_state.bool_game_finished) {
		return;
	}
	if(action==null) {
		this.send_action(action)
	} else {
	    setTimeout(this.send_action.bind(this, action), this.config.delay_millis);
	}
};
Singleplayer.prototype.send_action = function(action) {
	data = {
        'type': 'action',
        'action': action,
    }
    this.ws_send(data);
};


