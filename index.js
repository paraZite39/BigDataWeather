var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var kafka = require('kafka-node');
var HighLevelConsumer = kafka.HighLevelConsumer;
var Offset = kafka.Offset;
var Client = kafka.KafkaClient;

var raw_topic = 'real_time_viz_raw';
var avg_topic = 'real_time_viz_avg';
var avail_topic = 'real_time_viz_avail';

var raw_client = new Client('localhost:32181', "worker-" + Math.floor(Math.random() * 10000));
var avg_client = new Client('localhost:32181', "worker-" + Math.floor(Math.random() * 10000));
var avail_client = new Client('localhost:32181', "worker-" + Math.floor(Math.random() * 10000));

var raw_payloads = [{ topic: raw_topic }];
var avg_payloads = [{ topic: avg_topic }];
var avail_payloads = [{ topic: avail_topic }];

var raw_consumer = new kafka.Consumer(raw_client, raw_payloads);
var avg_consumer = new kafka.Consumer(avg_client, avg_payloads);
var avail_consumer = new kafka.Consumer(avail_client, avail_payloads);

var raw_offset = new Offset(raw_client);
var avg_offset = new Offset(avg_client);
var avail_offset = new Offset(avail_client);
var port = 3002;

app.get('/', function(req, res){
    res.sendfile('index.html');
});

io = io.on('connection', function(socket){
    console.log('a user connected');
    socket.on('disconnect', function(){
        console.log('user disconnected');
    });
});

raw_consumer = raw_consumer.on('message', function(message) {
    console.log("raw received: " + message.value);
    io.emit("raw_message", message.value);
});

avg_consumer = avg_consumer.on('message', function(message) {
    console.log("avg received: " + message.value);
    io.emit("avg_message", message.value);
});

avail_consumer = avail_consumer.on('message', function(message) {
    console.log("avail received: " + message.value);
    io.emit("avail_message", message.value);
});

http.listen(port, function(){
    console.log("Running on port " + port)
});
