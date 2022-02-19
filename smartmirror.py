from tkinter import *
from tkhtmlview import HTMLLabel
import locale
import threading
import time
import os
from datetime import datetime
import datetime as DateTime
import random
import webbrowser
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
import emotions_DB
from contextlib import contextmanager

LOCALE_LOCK = threading.Lock()

ui_locale = ''  # e.g. 'fr_FR' fro French, '' as default
time_format = 24  # 12 or 24
date_format = "%b %d, %Y"  # check python doc for strftime() for options
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18


@contextmanager
def setlocale(name):
    """
    Thread proof function to work with locale
    @param name: UI locale
    """
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


class Clock(Frame):
    """
    UI of the clock and update it according to the current time
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initialization of clock parameters (time, date)
        @param parent: UI frame
        """
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=('Helvetica', large_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.day_of_week1 = ''
        self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dayOWLbl.pack(side=TOP, anchor=E)
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.date1, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        self.tick()

    def tick(self):
        """
        Update the display time every 200 milliseconds
        """
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p')  # hour in 12h format
            else:
                time2 = time.strftime('%H:%M')  # hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            self.timeLbl.after(200, self.tick)


mental_illness_dict = {"depression": None, "manic_depression": None, "anxiety": None}
reports_dict = {"today": None, "yesterday": None, "day_before_yesterday": None}


class EmoImages(Frame):
    """
    UI of the images that displayed based on the current emotion
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the parameters required to display images from the Internet (URLs)
        @param parent: UI frame
        """
        Frame.__init__(self, parent)
        url = "https://static8.depositphotos.com/1008008/846/i/450/depositphotos" \
              "_8464756-stock-photo-luxury-chill-out-summer-bar.jpg"
        self.make_happy_url_list = ["https://vitapet.com/media/wutguhcs/questions-before-puppy-600x400.jpg",
                                    "http://cdn.shopify.com/s/files/1/0248/9516/0386/files/Hund_Fotolia_187023895_L_grande.jpg?v=1587047855"]
        self.chill_url_list = ["https://static.readytotrip.com/upload/information_system_24/1/5/2/item_1529126/information_items_1529126.jpg",
                               "https://cdn2.patriotgetaways.com/uploads/albums/7ff1ec22-68e6-11e8-9cf6-f23c91339e2c/grill-&-chill-private-deck-600x400.jpg"]
        self.calm_down_url_list = ["http://cdn.shopify.com/s/files/1/1417/3230/products/A0022321-Foster-Falls_grande.jpg?v=1575931829",
                                   "https://hiideemedia.com/wp-content/uploads/2021/03/Erawan-Waterfall-Thailand-600x400.jpg",
                                   "https://www.asiatravelgate.com/wp-content/uploads/2017/09/Phu-Cuong-Waterfall-Gia-Lai-Vietnam-005-600x400.jpg"]
        self.img_label = HTMLLabel(self, html=f"<img src='{url}'>")
        self.img_label.pack(side=TOP, fill="both", expand=True)
        self.img_of_emo()

    def img_of_emo(self):
        """
        Changes the image we want to display according to the current emotion
        """
        date_time = datetime.now()
        date = date_time.date()
        most_recently_emo = emotions_DB.get_most_recently_emo(date)
        if most_recently_emo == "Sad" or most_recently_emo == "Happy":
            rand_img = random.randint(0, len(self.make_happy_url_list)-1)
            url = self.make_happy_url_list[rand_img]
        elif most_recently_emo == "Neutral" or most_recently_emo == "Surprise":
            rand_img = random.randint(0, len(self.chill_url_list) - 1)
            url = self.chill_url_list[rand_img]
        elif most_recently_emo == "Angry":
            rand_img = random.randint(0, len(self.calm_down_url_list) - 1)
            url = self.calm_down_url_list[rand_img]
        else:
            url = "https://static.readytotrip.com/upload/information_system_24/1/5/2/item_1529126/information_items_1529126.jpg"

        self.img_label.set_html(f"<img src='{url}'>")
        self.img_label.after(5000, self.img_of_emo)  # calls itself every 5000 milliseconds (5 seconds)


class DailyReport(Frame):
    """
    UI of the emotional report
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the parameters required to display the report
        @param parent: UI frame
        """
        Frame.__init__(self, parent, bg='black')
        self.report = Label(self, font=('Helvetica', 24), fg="white", bg="black")
        self.report.pack(side=BOTTOM)

        mental_illness_thread = Thread(target=emo_job)
        mental_illness_thread.setDaemon(True)
        mental_illness_thread.start()

        self.day_report()

    def day_report(self):
        """
        Creates the information of the report based on the information available in the database
        """
        date_time = datetime.now()
        date = date_time.date()
        recently_emo = emotions_DB.get_most_recently_emo(date)
        reports_none = all([non is None for non in reports_dict.values()])  # Return the true if all the values in the dictionary are None
        mental_illness_none = all([non is None for non in mental_illness_dict.values()])
        if not recently_emo and reports_none and mental_illness_none:
            report_info = "Welcome to the smart emotional Mirror!"
        else:
            report_info = f"Daily info: \n"
            if recently_emo:
                report_info += f"Your most recently emotion is: {recently_emo} \n"
            if not reports_none:
                if reports_dict['today']:
                    report_info += f"today you were: {reports_dict['today']} \n"
                if reports_dict['yesterday']:
                    report_info += f"yesterday you were: {reports_dict['yesterday']} \n"
                if reports_dict['day_before_yesterday']:
                    report_info += f"in the day before yesterday you were: {reports_dict['day_before_yesterday']}"
            if not mental_illness_none:
                report_info += "\nMental health status: \n"
                if mental_illness_dict["depression"]:
                    report_info += f"{mental_illness_dict['depression']} \n"
                if mental_illness_dict["manic_depression"]:
                    report_info += f"{mental_illness_dict['manic_depression']} \n"
                if mental_illness_dict["anxiety"]:
                    report_info += f"{mental_illness_dict['anxiety']}"
            else:
                report_info += "\nMental health status: Stable (According to our data there " \
                               "are no signs of mental illness disease)"

        self.report.config(text=report_info)

        self.report.after(5000, self.day_report)  # calls itself every 5000 milliseconds (5 seconds)


def emo_job():
    """
    Scheduling every day at midnight will be done:
    • An attraction of the dominant emotion from the last days
    • Analysis of mental illness
    """
    scheduler = BlockingScheduler()
    now = datetime.now()
    date = datetime(now.year, now.month, now.day, 0, 0, 0)  # The current date in midnight
    stop_date = datetime(now.year+10, now.month, now.day, 0, 0, 0)  # 10 years from now
    while date < stop_date:
        date += DateTime.timedelta(days=1)
        # execute every day in midnight
        scheduler.add_job(get_report, "date", next_run_time=date)
        scheduler.add_job(check_mental_illness, "date", next_run_time=date)

    scheduler.start()


def get_report():
    """
    attraction of the dominant emotion from the last days
    """
    reports_dict["today"], reports_dict["yesterday"], reports_dict["day_before_yesterday"] = emotions_DB.emotion_report()


def check_mental_illness():
    """
    Analysis of mental illness
    """
    if emotions_DB.depression_analyser():
        depression = "You have characteristics that can be interpreted as depressive," \
               " it is recommended to be tested"
        mental_illness_dict["depression"] = depression
    else:
        mental_illness_dict["depression"] = None
    if emotions_DB.manic_depression_analyser():
        manic_depression = "You have characteristics that can be interpreted as manic depression," \
               " it is recommended to be tested"
        mental_illness_dict["manic_depression"] = manic_depression
    else:
        mental_illness_dict["manic_depression"] = None
    if emotions_DB.anxiety_analyser():
        anxiety = "You have characteristics that can be interpreted as anxiety," \
               " it is recommended to be tested"
        mental_illness_dict["anxiety"] = anxiety
    else:
        mental_illness_dict["anxiety"] = None


class FullscreenWindow:
    """
    UI of the entire window
    """
    def __init__(self):
        """
        Initialize all the UI parameters on the window
        """
        self.tk = Tk()
        # self.tk.attributes("-fullscreen", True)
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background='black')
        self.bottomFrame = Frame(self.tk, background='black')
        self.topFrame.pack(side=TOP, fill=BOTH, expand=YES)
        self.bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        # clock
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)
        # daily report
        self.daily_report = DailyReport(self.bottomFrame)
        self.daily_report.pack(side=BOTTOM)
        # emo images
        self.emo_images = EmoImages(self.topFrame)
        self.emo_images.pack(side=LEFT, anchor=NW)

    def toggle_fullscreen(self, event=None):
        """
        Toggling full screen
        """
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        """
        Exit full screen
        """
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"


def emo_music():
    """
    interval that plays music according to the current emotion
    """
    eve = threading.Event()
    music_timer = 45  # Activate once every 45 seconds
    while not eve.wait(music_timer):
        # os.system("killall -9 'Google Chrome'")
        youtube_urls = {"Make_happy": "https://www.youtube.com/watch?v=hT_nvWreIhg&list=PLhGO2bt0EkwvRUioaJMLxrMNhU44lRWg8",
                        "chill": "https://www.youtube.com/watch?v=25BkVBgFD9Y",
                        "relax": "https://www.youtube.com/watch?v=DGQwd1_dpuc"}
        date_time = datetime.now()
        date = date_time.date()
        most_recently_emo = emotions_DB.get_most_recently_emo(date)
        if most_recently_emo == "Sad" or most_recently_emo == "Happy":
            webbrowser.open_new(youtube_urls["Make_happy"])
        elif most_recently_emo == "Neutral" or most_recently_emo == "Surprise":
            webbrowser.open_new(youtube_urls["chill"])
        elif most_recently_emo == "Angry":
            webbrowser.open_new(youtube_urls["relax"])


def main():
    """
    Run the full window in UI loop
    """
    w = FullscreenWindow()
    w.tk.mainloop()


def emo_main():
    """
    Calls the emotion detection function
    """
    os.system('python emotion_detection.py')


if __name__ == '__main__':
    emo_thread = Thread(target=emo_main)
    emo_thread.start()

    music_thread = Thread(target=emo_music)
    music_thread.setDaemon(True)
    music_thread.start()

    main()
