class Emotion:
    """
    Defines the property of emotion (the emotion, date)
    """

    def __init__(self, emotionID, emotion, date, time):
        """
        Initialize Emotion parameters
        @param emotionID: ID of The emotion
        @param emotion: ID type (name)
        @param date: date in format: "Y-M-D"
        @param time: time in format: "H:M:S"
        """
        self.emotionID = emotionID
        self.emotion = emotion
        self.date = date
        self.time = time

    @property
    def emotional_status(self):
        """
        string of the emotion status
        @return: all class properties
        """
        return f"'{self.emotionID}', {self.emotion}', '{self.date}', '{self.time}'"

    def __repr__(self):
        """
        printable representation of the Emotion object
        @return: all class properties
        """
        return f"Emotion('{self.emotionID}', {self.emotion}', '{self.date}', '{self.time}')"

