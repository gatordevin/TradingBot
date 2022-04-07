import websocket
import json
import threading
import time


def send_json_request(ws , request):
    ws.send(json.dumps(request))

def receive_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)

def heartbeat(interval, ws):
    print("Heartbeat begin")
    while True:
        time.sleep(interval)
        heartbeat_json = {
            "op" : 1,
            "d" : "null"
        }
        send_json_request(ws, heartbeat_json)
        print("heartbeat sent")

ws = websocket.WebSocket()
ws.connect("wss://gateway.discord.gg/?v=6&encording=json")

event = receive_json_response(ws)

heartbeat_interval = event["d"]["heartbeat_interval"]/1000

heartbeat_thread = threading.Thread(target=heartbeat,args=(heartbeat_interval, ws))
heartbeat_thread.setDaemon(True)
heartbeat_thread.start()

token = "MzAyMTc0OTAwNjYyMDQyNjI1.YktqzQ.rfm-XEyLMet3uUXb0YSyHYVlvPU"
payload = {
    "op" : 2,
    "d" : {
        "token" : token,
        "properties" : {
            "$os" : "windows",
            "$browser" : "chrome",
            "$device" : "pc"
        }
    }
}
send_json_request(ws, payload)

while True:
    event = receive_json_response(ws)
    try:
        print( event["d"]["author"]["username"] + ": " + event["d"]["content"])
        print(event["d"]["author"]["id"])
        op_code = event("op")
        if op_code == 11:
            print("heartbeat_recieved")
    except:
        pass