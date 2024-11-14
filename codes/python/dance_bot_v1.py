from bluepy import btle
import paho.mqtt.client as mqtt
from buildhat import Motor
from time import sleep
import vlc
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class MotorController:
    def __init__(self):
        self.right_arm = Motor('A')
        self.left_arm = Motor('B')

    def combo(self):
        self._move_arms(speed_right=-100, speed_left=100)

    def back(self):
        self._move_arms(speed_right=100, speed_left=-100)

    def both(self):
        self._move_arms(speed_right=-100, speed_left=100, blocking=False)

    def backb(self):
        self._move_arms(speed_right=100, speed_left=-100, blocking=False)

    def _move_arms(self, speed_right, speed_left, duration=1.3, blocking=True):
        self.right_arm.run_for_seconds(duration, speed=speed_right, blocking=blocking)
        self.left_arm.run_for_seconds(duration, speed=speed_left, blocking=blocking)


class SpotifyController:
    def __init__(self, client_id, client_secret, redirect_uri, scope):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
                open_browser=False
            )
        )

    def start_playback(self, device_id, uri):
        self.sp.start_playback(device_id=device_id, uris=[uri])


class VideoPlayer:
    def __init__(self, video_path):
        self.player = vlc.MediaPlayer(video_path)

    def play(self):
        self.player.play()
        self.player.set_fullscreen(True)

    def is_finished(self):
        return self.player.get_state() == vlc.State.Ended

    def stop(self):
        self.player.stop()


def mqtt_publish(client, topic, message):
    client.publish(topic, message)


def handle_movement(move, mqtt_client, spotify_controller, motor_controller):
    if move == 1:
        mqtt_publish(mqtt_client, "dance/lights", "on")
        print("on")
        spotify_controller.start_playback(device_id, 'spotify:track:5bXGg3XcbEGClkdZ8XYTkI')
        video = VideoPlayer('/home/pi/Desktop/model4/ink1.mp4')
        video.play()
        for _ in range(2):
            motor_controller.combo()
            sleep(0.5)
            motor_controller.back()
            sleep(0.5)
        wait_for_video(video)

    elif move == 2:
        mqtt_publish(mqtt_client, "dance/lights", "on2")
        print("on2")
        spotify_controller.start_playback(device_id, 'spotify:track:1o7D1gLUgpFR3eJfI')
        video = VideoPlayer('/home/pi/Desktop/model4/ink4.mp4')
        video.play()
        for _ in range(2):
            motor_controller.both()
            sleep(2)
            motor_controller.backb()
            sleep(1)
        wait_for_video(video)

    elif move == 3:
        mqtt_publish(mqtt_client, "dance/lights", "on3")
        print("on3")
        spotify_controller.start_playback(device_id, 'spotify:track:1c39AwcrkN9srI7Az5662I')
        video = VideoPlayer('/home/pi/Desktop/model4/magic.mp4')
        video.play()
        for _ in range(2):
            motor_controller.combo()
            sleep(0.5)
            motor_controller.back()
            sleep(0.5)
        wait_for_video(video)

def wait_for_video(video):
    while not video.is_finished():
        sleep(1)
    video.stop()
    sleep(8)  # Give some time before the next action


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def handleNotification(self, cHandle, data):
        num = int.from_bytes(data, byteorder='big')
        self.callback(num)


# Initialization
broker_address = "192.168.0.0"
device_id = ""
client_id = ""
client_secret = ""
redirect_uri = "http://localhost:8080"
scope = "user-read-playback-state,user-modify-playback-state"

mqtt_client = mqtt.Client("P1")
mqtt_client.connect(broker_address)

spotify_controller = SpotifyController(client_id, client_secret, redirect_uri, scope)
motor_controller = MotorController()

p = btle.Peripheral("1a:b4:c0:25:3a:aa")
p.setDelegate(MyDelegate(lambda new_value: handle_movement(new_value, mqtt_client, spotify_controller, motor_controller)))

svc = p.getServiceByUUID("81c30e5c-1101-4f7d-a886-de3e90749161")
ch = svc.getCharacteristics("81c30e5c-2101-4f7d-a886-de3e90749161")[0]

setup_data = b"\x01\00"
p.writeCharacteristic(ch.valHandle + 1, setup_data)

# Main loop
while True:
    if p.waitForNotifications(1.0):
        continue
    print("Waiting...")
