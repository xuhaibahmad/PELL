import smtplib
import time
from pell.assistant.text_to_speech import talk, listen
import sys
import os


class EmailAction:

    def __init__(self, command, subject=None, message=None, receiver=None):
        self.command = command
        self.subject = subject
        self.message = message
        self.receiver = receiver
        self.email = os.getenv("gmail_email")
        self.password = os.getenv("gmail_password")

    def execute(self):
        # Ask for recepient only when not provided in the command
        if self.receiver == None:
            talk('Who do you want to send it to?')
            time.sleep(3)
            self.receiver = listen()
        # Ask for subject only when not provided in the command
        if self.subject == None:
            talk('What is the subject?')
            time.sleep(3)
            self.subject = listen()
        # Ask for message only when not provided in the command
        if self.message == None:
            talk('What should I say?')
            time.sleep(3)
            self.message = listen()

        content = 'Subject: {}\n\n{}'.format(self.subject, self.message)

        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(self.email, self.password)

        # send message
        mail.sendmail(self.email, self.receiver, content)

        # end mail connection
        mail.close()

        talk('Email sent.')
        sys.exit('Email sent.')


if __name__ == "__main__":
    test_email = os.getenv("test_email")
    EmailAction(
        "Send email to myself",
        "PELL",
        "This is a test message from PELL",
        test_email
    ).execute()
