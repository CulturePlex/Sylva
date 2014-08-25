// From: http://stackoverflow.com/questions/15308371

function EventObject(name){
  this.name = name;
  this.callbacks = [];
}

EventObject.prototype.registerCallback = function(callback){
  debugger;
  this.callbacks.push(callback);
};

Event.prototype.removeCallback = function(callback){
  var index = this.callbacks.indexOf(callback);
  if (index > -1) {
    this.callbacks.splice(index, 1);
  }
}


function Reactor(){
  this.events = {};
}

Reactor.prototype.registerEvent = function(eventName){
  var event = new EventObject(eventName);
  this.events[eventName] = event;
};

Reactor.prototype.dispatchEvent = function(eventName, eventArgs){
  this.events[eventName].callbacks.forEach(function(callback){
    callback(eventArgs);
  });
};

Reactor.prototype.addEventListener = function(eventName, callback){
  this.events[eventName].registerCallback(callback);
};

Reactor.prototype.removeEventListener = function(eventName, callback) {
  this.events[eventName].removeCallback(callback);
}
