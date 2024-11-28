function Simulation(config) {
    this.config = config
    this.game = new Game(config.game_config);
    this.ws = null;
    this.main();
};
Simulation.prototype.main = function(){
    this.init_websocket();
};
Simulation.prototype.init_websocket = function(){
    this.ws = new WebSocket(this.config.ws_endpoint);
    this.ws.onopen = this.ws_onopen.bind(this);
    this.ws.onmessage = this.ws_onmessage.bind(this);
}
Simulation.prototype.ws_onopen = function(event) {
    this.add_log('> connected');
};
Simulation.prototype.ws_send = function(data) {
    this.add_log('< '+data['type']);
    this.ws.send(JSON.stringify(data))
};
Simulation.prototype.ws_onmessage = function(event) {
    var data = JSON.parse(event.data);
    this.add_log('> '+data.type);
    switch(data['type']) {
        case 'update':
    		this.add_log(data['state']);
    		this.game.set_player_state(data['state']);
    		this.apply_action(data['state']['selected_action']);
            break;
    }
};
Simulation.prototype.add_log = function(msg) {
    //console.log(msg);
};

Simulation.prototype.apply_action = function(action) {
	if(this.game.player_state.bool_game_finished) {
		return;
	}
	if(action==null) {
		this.send_action(action)
	} else {
	    setTimeout(this.send_action.bind(this, action), this.config.delay_millis);
	}
};
Simulation.prototype.send_action = function(action) {
	data = {
        'type': 'action',
        'action': action,
    }
    this.ws_send(data);
};


