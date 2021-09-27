from keras.models import load_model
from time import sleep
from keras.preprocessing.image import img_to_array
from keras.preprocessing import image
from datetime import datetime
import datetime as DateTime
import time as time_counter
from emotion_class import Emotion
import emotions_DB as db
import cv2
import numpy as np


def emo_main():
    """
    Detect the current emotion
    """
    def if_insert_emotion(timer, pre_emo, emo):
        """
        Checks if the current emotion exists for at least a minimal amount of time (2 seconds)
        in order to put it into the database
        @param timer: Timer to check if the minimum time has elapsed
        @param pre_emo: Previous emotion
        @param emo: Current emotion
        @return: True if the minimum time has elapsed, False otherwise
        """
        if pre_emo != emo:
            timer[0] = time_counter.time()
        else:
            if (time_counter.time() - timer[0]) >= 2:
                # If after 2 seconds the emotion remains he gets permission to enter the DB
                timer[0] = time_counter.time()
                return True
        return False

    def log_file(time, prediction, id, emotion):
        """
        Write to log file
        @param time: time in format: "Y-M-D H:M:S"
        @param prediction: list of emotion prediction results
        @param id: ID of the emotion with the max prediction
        @param emotion: emotion name
        """
        with open('emotion_log.log', 'a') as log:
            log.write(f"\ntime: {time}")
            log.write(f"\nprediction = {prediction}")
            log.write(f"\nprediction max = {id}")
            log.write(f"\nlabel = {emotion}")
            log.write("\n\n")

    face_classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
    classifier = load_model('Emotion_Detection.h5')

    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    cap = cv2.VideoCapture(0)

    start_timer = [time_counter.time()]
    pre_emotionID = None
    emotionID = None

    while True:
        # Grab a single frame of video
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            face_gray = gray[y:y + h, x:x + w]
            face_gray = cv2.resize(face_gray, (48, 48), interpolation=cv2.INTER_AREA)

            if np.sum([face_gray]) != 0:
                face = face_gray.astype('float') / 255.0
                face = img_to_array(face)
                face = np.expand_dims(face, axis=0)

                preds = classifier.predict(face)[0]
                preds[2] *= 0.65  # Neutral curve fitting
                pre_emotionID = emotionID
                emotionID = preds.argmax()
                label = class_labels[emotionID]
                date_time = datetime.now()
                date = date_time.date()
                time = date_time.time().__str__()
                # datetime.fromisoformat(time) // Converse back to datetime object
                emo = Emotion(int(emotionID), label, date, time)
                if if_insert_emotion(start_timer, pre_emotionID, emotionID):
                    db.insert_emotion(emo)
                log_file(date_time, preds, emotionID, label)
                label_position = (x, y)
                cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            else:
                cv2.putText(frame, 'No Face Found', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.imshow('Emotion Detector', frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q") or key == ord("Q"):
            break

    cap.release()
    cv2.destroyAllWindows()


emo_main()
