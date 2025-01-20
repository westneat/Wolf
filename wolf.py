import game as gm
import time
import datetime

wolf = gm.Game([47, 157, 62, 101, 45, 65, 7, 40, 4, 8, 100, 82, 128, 67, 306, 18], "Wolfbot Beta Deux")

wolf = gm.Game([47, 157, 62, 101, 45, 65, 7, 40, 4, 8, 100, 82, 128, 67, 306, 18], "Wolfbot Beta Threes")

#wolf.assign_player_numbers()
#wolf.assign_roles()

#wolf.resume("Wolfbot Beta Deux")

wolf.resume("Wolfbot Beta Threes")

while not wolf.game_over:
    wolf.start_night()
    new_thread = False
    while datetime.datetime.now() < wolf.night_close_tm:
        if wolf.game_over:
            break
        print("Running nightly check")
        wolf.run_night_checks()
        print("Completed")
        if datetime.datetime.now() < wolf.night_close_tm - datetime.timedelta(minutes=5):
            time.sleep(300)
        if (wolf.night != 1 and datetime.datetime.now() > wolf.night_close_tm - datetime.timedelta(hours=1)
                and not new_thread):
            new_thread = True
            wolf.day_thread.gameover()
            wolf.day_thread.create_thread(f"{wolf.game_title} Day {wolf.night}", wolf.day_post())
            wolf.day_thread.stick_thread()
            wolf.day_thread.lock_thread()
        elif wolf.night == 1:
            new_thread = True
    wolf.run_night_checks()
    if not new_thread:
        new_thread = True
        wolf.day_thread.gameover()
        wolf.day_thread.create_thread(f"{wolf.game_title} Day {wolf.night}", wolf.day_post())
        wolf.day_thread.stick_thread()
        wolf.day_thread.lock_thread()
    wolf.end_night()
    wolf.start_day()
    while datetime.datetime.now() < wolf.day_close_tm:
        if wolf.game_over:
            break
        print("Running daily check")
        wolf.run_day_checks()
        print("Completed")
        if datetime.datetime.now() < wolf.day_close_tm - datetime.timedelta(minutes=5):
            time.sleep(300)
    wolf.run_day_checks()
    wolf.end_day()

