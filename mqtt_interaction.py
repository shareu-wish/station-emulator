import paho.mqtt.client as mqtt
from threading import Timer
from time import sleep


"""
wish
- station1
    - slot1
        - lock: (status: closed/opened, command: open/close)
        - has_umbrella: (status: y/n)
"""

stations_data = {}


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("wish/#")


def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    # wish/station2/slot17/lock
    topic_parts = msg.topic.split("/")
    # print(topic_parts[1][:7])
    if topic_parts[1][:7] == "station" and topic_parts[2][:4] == "slot" and topic_parts[3]:
        station_id = int(topic_parts[1][7:])
        slot_id = int(topic_parts[2][4:])
        if station_id not in stations_data:
            stations_data[station_id] = {}
        if slot_id not in stations_data[station_id]:
            stations_data[station_id][slot_id] = {}
        stations_data[station_id][slot_id][topic_parts[3]] = msg.payload.decode()
        
        update_data_callback(stations_data)



mqttc = None
update_data_callback = None


def connect(host, port, username, password, callback):
    global mqttc, stations_data, update_data_callback, self_object
    update_data_callback = callback

    stations_data = {}
    if mqttc and mqttc.is_connected():
        mqttc.disconnect()
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.username_pw_set(username, password)
    mqttc.connect(host, port)
    
    mqttc.loop_start()


def put_umbrella(station_id, slot_id):
    mqttc.publish(f"wish/station{station_id}/slot{slot_id}/has_umbrella", "y", retain=True)

def take_umbrella(station_id, slot_id):
    mqttc.publish(f"wish/station{station_id}/slot{slot_id}/has_umbrella", "n", retain=True)

def set_lock(station_id, slot_id, lock):
    mqttc.publish(f"wish/station{station_id}/slot{slot_id}/lock", lock, retain=True)

# if __name__ == "__main__":
#     connect()

