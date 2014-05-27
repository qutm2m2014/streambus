#!/usr/bin/env python


import multiprocessing as mp
import paho.mqtt.client as paho
import sys
# import collections
# import time
import zmq
import jsonpickle


# class EventSink():
#     def __init__(self, *queue_uris):
#         self.context = zmq.Context()
#         self.poller = zmq.Poller()
#         for uri in queue_uris:
#             rec = self.context.socket(zmq.SUB)
#             rec.connect(uri)
#             rec.setsockopt(zmq.SUBSCRIBE, "")
#             self.poller.register(rec, zmq.POLLIN)

#     def run(self):
#         while True:
#             socks = dict(self.poller.poll())



# # Manipulates Event Streams
# class EventWork():
#     def __init__(self, queue_uris):
#         pass


# class EventVent():
#     pass
class Event():

    def __init__(self, source_atom, source_sensor, raw_data):
        self.atom = source_atom
        self.sensor = source_sensor
        self.data = raw_data

    def __str__(self):
        return "Source: %s\t Sensor: %s\t Data: %s\t" % (self.atom,
                                                         self.sensor,
                                                         self.data)

    def json(self):
        return jsonpickle.encode(self, unpicklable=False)


class MQTTVent():

    def __init__(self,
                 topic="#",
                 mqtt_broker_address="localhost",
                 mqtt_broker_port=1884,
                 bind_addr=""):
        self.bind_addr = bind_addr
        self.topic = topic
        self.mqtt_broker_port = mqtt_broker_port
        self.mqtt_broker_address = mqtt_broker_address

    def start(self):

        # Setup MQTT Subscriber
        mqttc = paho.Client()
        mqttc.connect(self.mqtt_broker_address, self.mqtt_broker_port, 60)
        mqttc.subscribe(self.topic, 0)

        # Setup ZeroMQ
        context = zmq.Context()
        ventilator_send = context.socket(zmq.PUB)
        ventilator_send.bind(self.bind_addr)

        def on_message(client, obj, message):
            topic = message.topic.split("/")
            event = Event(source_atom=topic[0],
                          source_sensor=topic[1],
                          raw_data=message.payload)
            ventilator_send.send(event)

        mqttc.on_message = on_message

        rc = 0
        while rc is 0:
            mqttc.loop()


class DatabaseCollector():
    def __init__(self, connect_addr):
        # self.db_pool = psycopg2.pool.ThreadedConnectionPool(3, 10)
        self.connect_addr = connect_addr

    def start(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUBSCRIBE)
        socket.connect(self.connect_addr)
        print "Connected to %s. Recieving Data" % (self.connect_addr)
        i = 0
        while True:
            i = i + 1
            event = socket.recv_pyobj()
            print str(i) + " DB RECV " + str(event)


class SpikeDetector():
    def __init__(self, connect_addr, maximum):
        self.connect_addr = connect_addr
        self.maximum = maximum

    def start(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.connect_addr)
        print "Firing on %d" % (self.maximum)
        i = 0
        while True:
            i = i + 1
            event = socket.recv_pyobj()
            print str(i) + " SD RECV " + str(event)
            # print type(event.data)
            # print float(event.data)
            # if int(event.data) > int(self.maximum):
            #     print "Event Data %d is greater than maxium %d" % (int(event.data), int(self.maximum))

# class SpikeDetector():
#     def __init__(self, maximum, in_queue):
#         assert maximum == int(maximum), "Maximum must be an integer"
#         self.maximum = maximum
#         if in_queue is None:
#             self.in_queue = mp.Queue()
#         else:
#             self.in_queue = in_queue
#         self.out_queue = mp.Queue()

#     def get_out_queue(self):
#         return self.out_queue

#     def start(self):
#         p = mp.Process(target=self.run, args=(self.in_queue, self.out_queue))
#         p.start()

#     def run(self, in_queue, out_queue):
#         while True:
#             try:
#                 n = in_queue.get(timeout=1)
#                 print n
#             except Empty:
#                 continue

#             if n > self.maximum:
#                 out_queue.put("SPIKED")


# class SMA():
#     def __init__(self, period):
#         assert period == int(period) and period > 0, \
#             "Period must be an integer >0"
#         self.period = period
#         self.stream = collections.deque()

#     def run(self, in_queue, out_queue):

#         while True:
#             try:
#                 n = in_queue.get(timeout=1)
#             except Empty:
#                 continue
#             stream = self.stream
#             stream.append(n)    # appends on the right
#             streamlength = len(stream)

#             if streamlength > self.period:
#                 stream.popleft()
#                 streamlength -= 1

#             if streamlength == 0:
#                 out_queue.put(0)
#             else:
#                 out_queue.put(sum(stream) / streamlength)


def main():
    mp.Process(target=MQTTVent(bind_addr="tcp://127.0.0.1:5558").start).start()
    mp.Process(target=DatabaseCollector(connect_addr="tcp://127.0.0.1:5558").start).start()
    mp.Process(target=SpikeDetector("tcp://127.0.0.1:5558", 25).start).start()

if __name__ == "__main__":
    sys.exit(main())