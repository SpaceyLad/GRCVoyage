import csv
import time as t
import threading
import pandas as pd
import dash_logic, calculations, config as conf


def import_cases():
    global df
    df = pd.read_csv(conf.cases_file)
    return csv.reader(open(conf.cases_file, "r"), delimiter=",", quotechar="|")


def refresh_msg(c):
    print(f"Update interval nr: {c}")
    t.sleep(conf.refresh_seconds)


def loop():
    global cases

    c = 1
    while 1:
        cases = import_cases()
        dash_logic.refresh_dashboard()
        refresh_msg(c)
        c = c + 1


def run_loop():
    try:
        # Create threads
        loop_thread = threading.Thread(target=loop)

        # Start thread
        loop_thread.start()

    except:
        print("Error: unable to start thread")


@dash_logic.server.route("/")
def index():
    return "Welcome! Visit /dashboard for the dashboard."


if __name__ == "__main__":

    # Start background update thread
    run_loop()

    # Start server
    dash_logic.app.run_server()
