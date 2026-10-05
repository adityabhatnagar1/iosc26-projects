"""Five known phishing and five known legitimate emails used for the demonstration."""

EMAILS = [
    # ---- Known phishing ----
    dict(label="PHISHING", name="P1 PayPal lookalike",
         **{"from": "PayPal Security <support@paypa1-secure.com>"},
         subject="Urgent: Your account has been suspended",
         body='Dear Customer,\nWe detected unauthorized activity. Your account will be suspended within 24 hours. '
              'Verify your password now: <a href="http://paypa1-secure.com/login">www.paypal.com/verify</a>'),
    dict(label="PHISHING", name="P2 Microsoft 365 password expiry",
         **{"from": "IT Helpdesk <admin@mail-helpdesk.ru>"},
         subject="Microsoft 365 password expires today",
         body='Dear user, your Microsoft password expires today. Confirm your password immediately: '
              '<a href="http://192.168.45.10/o365/login">https://login.microsoftonline.com</a>'),
    dict(label="PHISHING", name="P3 DHL parcel + attachment",
         **{"from": "DHL Express <track@dhl-delivery-notice.info>"},
         subject="Package on hold - action required",
         body="Your parcel could not be delivered. See attached label and track here: https://bit.ly/3xYz12 "
              "Final notice before return.",
         attachments=["DHL_Label.pdf.zip"]),
    dict(label="PHISHING", name="P4 CEO gift-card fraud (BEC)",
         **{"from": "Rakesh Mehta <rakesh.mehta.ceo@gmail.com>"},
         reply_to="r.mehta.private@outlook.com",
         subject="Quick favor",
         body="Are you at your desk? I'm in a meeting and need you to buy 5 gift card codes for clients. "
              "Do it right away and send me the codes. I will reimburse you."),
    dict(label="PHISHING", name="P5 Lottery scam",
         **{"from": "Prize Dept <claims@intl-lottery-win.biz>"},
         subject="CONGRATULATIONS!!! You have won",
         body="Dear Winner, you have won $1,000,000 in the international lottery! Claim your prize! "
              "Send your card number and re-enter your identity details to claim."),
    # ---- Known legitimate ----
    dict(label="LEGIT", name="L1 GitHub notification",
         **{"from": "GitHub <noreply@github.com>"},
         subject="[repo] New pull request #42",
         body='Tejas opened a pull request. View it here: <a href="https://github.com/org/repo/pull/42">'
              'https://github.com/org/repo/pull/42</a>'),
    dict(label="LEGIT", name="L2 Amazon shipping",
         **{"from": "Amazon.in <shipment-tracking@amazon.in>"},
         subject="Your Amazon order has shipped",
         body='Hello Tejas, your package is on the way and arrives Thursday. '
              'Track: <a href="https://www.amazon.in/gp/your-account/order-details">Track package</a>'),
    dict(label="LEGIT", name="L3 Team meeting",
         **{"from": "Priya Sharma <priya.sharma@usar.ipu.ac.in>"},
         subject="Hackathon sync tomorrow 4pm",
         body="Hi team, please send your slides before tomorrow's sync. Agenda: demo, timeline, Q&A. Thanks!"),
    dict(label="LEGIT", name="L4 Bank alert (urgent tone)",
         **{"from": "HDFC Bank <alerts@hdfcbank.net>"},
         subject="Important: unusual login attempt blocked",
         body='Hello Tejas, we blocked a login attempt from a new device. If this was not you, please act now and '
              'call the number on the back of your card. Never share your OTP. '
              'Details: <a href="https://www.hdfcbank.com/security">https://www.hdfcbank.com/security</a>'),
    dict(label="LEGIT", name="L5 Google Calendar invite",
         **{"from": "Google Calendar <calendar-notification@google.com>"},
         subject="Invitation: Ambassador sync @ Fri 5pm",
         body='You have been invited. <a href="https://calendar.google.com/event?eid=abc">View event</a>'),
]
