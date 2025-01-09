import game as gm
import time
import datetime
import sys

wolf = gm.Game(sys.argv[1], sys.argv[2])
wolf.assign_player_numbers()
wolf.assign_roles()

while not wolf.game_over:
    wolf.start_night()
    while datetime.datetime.now() < wolf.night_close_tm:
        if wolf.game_over:
            break
        if datetime.datetime.now() < datetime.datetime.now() - datetime.timedelta(minutes=10):
            wolf.run_night_checks()
            time.sleep(300)
    wolf.run_night_checks()
    wolf.end_night()
    wolf.start_day()
    while datetime.datetime.now() < wolf.day_close_tm:
        if wolf.game_over:
            break
        if datetime.datetime.now() < datetime.datetime.now() - datetime.timedelta(minutes=10):
            wolf.run_day_checks()
            time.sleep(300)
    wolf.run_day_checks()
    wolf.end_day()
