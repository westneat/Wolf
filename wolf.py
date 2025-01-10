import game as gm
import time
import datetime

wolf = gm.Game([47, 157, 62, 101, 95, 65, 7, 40, 4, 8, 100, 82, 54, 67, 306, 18], "Wolfbot Beta Game")

# wolf.assign_player_numbers()
# wolf.assign_roles()
wolf.resume("Wolfbot Beta Game")

while not wolf.game_over:
    wolf.start_night()
    while datetime.datetime.now() < wolf.night_close_tm:
        if wolf.game_over:
            break
        print("Running nightly check")
        wolf.run_night_checks()
        print("Completed")
        time.sleep(300)
    wolf.run_night_checks()
    wolf.end_night()
    wolf.start_day()
    while datetime.datetime.now() < wolf.day_close_tm:
        if wolf.game_over:
            break
        print("Running daily check")
        wolf.run_day_checks()
        print("Completed")
        time.sleep(300)
    wolf.run_day_checks()
    wolf.end_day()
