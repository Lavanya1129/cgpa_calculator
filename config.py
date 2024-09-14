from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use the appropriate port for your provider
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nlavanya1129@gmail.com'
app.config['MAIL_PASSWORD'] = 'yducbyigrhplcwby'

mail = Mail(app)

@app.route('/')
def send_email():
    msg = Message('Subject', sender='nlavanya1129@gmail.com', recipients=['r190208@rguktrkv.ac.in'])
    msg.body = 'Body of the email'
    mail.send(msg)
    return 'Email sent'

if __name__ == '__main__':
    app.run(debug=True)
