import ctypes
import datetime as dt
import logging
import pause
import psutil
import sys
import time


logging.basicConfig(level=logging.DEBUG, filename="blocker.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

# Start and end hours for free time
START = 18
END = 1

# Convert to time objects
START_TIME = dt.time(hour=START)
END_TIME = dt.time(hour=END)

BASIC_PAUSE = 5
SHORT_PAUSE = 2

MessageBox = ctypes.windll.user32.MessageBoxW


def free_time():
    now = dt.datetime.now().time()
    if START_TIME < END_TIME:
        return START_TIME <= now < END_TIME
    else:
        # Between midnight
        return now >= START_TIME or now < END_TIME


def main():
    logging.info("Script start")
    try:
        with open("names.txt") as file:
            proc_to_block = file.read().splitlines()
    except EnvironmentError as e:
        logging.error(e)
        return

    blocked = False
    allowed_process = proc_to_block[-1]

    while True:
        if free_time():
            logging.debug("Start free time")
            now = dt.datetime.now()
            # Calculate the time until the free time ends
            countdown = (dt.timedelta(hours=24) - (now - now.replace(hour=END,
                         minute=0, second=0, microsecond=0))).total_seconds() % (24 * 3600)
            logging.debug(f"Pausing for {countdown} s")
            pause.seconds(countdown)    # Pause until END time

            # Pause for a while if a certain process is still running
            if allowed_process in [proc.name() for proc in psutil.process_iter()]:
                proc.wait()
                logging.debug(f"Pausing for {SHORT_PAUSE} min")
                pause.minutes(SHORT_PAUSE)

            for proc in psutil.process_iter():
                name = proc.name()
                if name in proc_to_block:
                    logging.debug(f"{name} is still running")
                    MessageBox(None, "5 minutes left.", "Program Blocker")
                    logging.debug(f"Pausing for {BASIC_PAUSE} min")
                    pause.minutes(BASIC_PAUSE)
                    break

            logging.debug("End free time")

        else:
            for proc in psutil.process_iter():
                if proc.name() in proc_to_block:
                    proc.kill()
                    logging.info(f"{proc.name()} stopped")
                    blocked = True

            if blocked:
                blocked = False
                MessageBox(
                    None,
                    "Not free time yet!",
                    "Program Blocker",
                    0x1000
                )

        time.sleep(30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped by user")
        sys.exit(0)
