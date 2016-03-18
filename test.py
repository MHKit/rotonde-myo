#!/usr/bin/python

import signal
import sys
import json

import threading
import websocket

#
# Myo stuffs
#

from PyoConnect import *
myo = Myo(sys.argv[1] if len(sys.argv) >= 2 else None)

def myo_thread():
	myo.connect()
	myo.use_lock = False
	myo.unlock("hold")
	myo.vibrate(1)
	while True:
		myo.run()
		myo.tick()

#
# Myo events

def onPoseEdge(pose, edge):
	print("onPoseEdge: " + pose + ", " + edge)
	send_event("MYO_POSE_EDGE", {"pose": pose, "edge": edge})

def onUnlock():
	print("Unlock ! ")
	send_event("MYO_UNLOCK", {})

def onLock():
	print("Lock ! ")
	send_event("MYO_LOCK", {})

period_n = 0
def onPeriodic():
	global period_n
	period_n += 1
	if (period_n % 5) != 0:
		return
	#print({"roll": myo.getRoll(),"pitch": myo.getPitch(),"yaw": myo.getYaw(),"gyro": myo.getGyro(),"accell": myo.getAccel()})
 	send_event("MYO_PERIODIC", {"roll": myo.getRoll(),"pitch": myo.getPitch(),"yaw": myo.getYaw(),"gyro": myo.getGyro(),"accell": myo.getAccel()})

def onWear(arm, xdirection):
	print("Myo wear!")
	send_event("MYO_WEAR", {"arm": arm, "xdirection": xdirection})

def onUnwear():
	print("Myo unwear! ")
	send_event("MYO_UNWEAR", {})



myo.onPoseEdge = onPoseEdge
myo.onLock = onLock
myo.onUnlock = onUnlock
myo.onWear = onWear
myo.onUnwear = onUnwear
myo.onPeriodic = onPeriodic
#myo.onEMG = onEMG
#myo.onBoxChange = onBoxChange


#
# Rotonde stuffs
#

# send helpers

def send_definition(typ, name, fields):
	print("Sending definition " + name)
	global ws
	d = json.dumps({"type":"def","payload":{"identifier": name,"type": typ,"fields": fields}})
	if ws.sock.connected == True:
		ws.send(d)


def send_action(name, data):
	print("Sending action " + name)

def send_event(name, data):
	global ws
	d = json.dumps({"type":"event", "payload": {"identifier": name, "data": data}})
	if ws.sock.connected == True:
		ws.send(d)


def send_subscribe(name):
	print("Sending subscribe " + name)

# receive helpers

def onRotondeMyoVibrate(action):
	print "Vibrate !"

action_handlers = {
	"MYO_VIBRATION": onRotondeMyoVibrate
}

#
# Websocket stuffs
#

def on_message(ws, message):
	packet = json.loads(message)
	print message
	if packet["type"] == "action":
		action = packet["payload"]
		print "received action " + action["identifier"]
		handler = action_handlers[action["identifier"]]
		if handler != None:
			handler(action["data"])
	elif packet["type"] == "def":
		print "received definition " + packet["payload"]["identifier"]

def on_error(ws, error):
	print error
	sys.exit(0)

def on_close(ws):
	print "Closed"
	sys.exit(0)

def on_open(ws):
	print "Connected"
	send_definition("action", "MYO_VIBRATION", [{"name":"vibrationType","type":"number","units":""}])

websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://rotonde:4224/",
			  on_message = on_message,
			  on_error = on_error,
			  on_close = on_close)
ws.on_open = on_open

def ws_thread():
	ws.run_forever()

#
# Threading stuffs
#

tmyo = threading.Thread(target=myo_thread)
tmyo.daemon = True
tmyo.start()

tws = threading.Thread(target=ws_thread)
tws.daemon = True
tws.start()

def signal_handler(signal, frame):
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.pause()
