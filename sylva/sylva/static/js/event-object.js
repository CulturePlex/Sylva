// From: http://stackoverflow.com/questions/15308371

function EventObject(name){
  this.name = name;
  this.callbacks = [];
}

EventObject.prototype.registerCallback = function(callback){
  this.callbacks.push(callback);
};

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
