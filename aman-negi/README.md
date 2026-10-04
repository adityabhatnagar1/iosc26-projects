# Project Title
# Basic Phishing Email Pattern Detector

> A rule-based web application that analyzes email content for common phishing indicators and classifies the message as phishing or legitimate without using machine learning.

**Track:** [i5]  
**Candidate:** Aman Negi  
**Github Username**: [AmanNegi778]  
**Phone Number**: [9667924411]  
**Email ID**: [aman67work@gmail.com]  

---

## 1. Overview

### What & Why
This project is a basic phishing email pattern detector built using HTML, CSS, and JavaScript.

The detector analyzes the content of an email and searches for common phishing indicators such as urgent or threatening language, requests for sensitive information, account verification requests, suspicious URLs, IP-address URLs, dangerous attachments, generic greetings, excessive exclamation marks, and suspicious link requests.

A weighted rule-based scoring system is used to determine the risk level of an email.

If the final risk score is 5 or higher, the email is classified as **PHISHING**. Otherwise, it is classified as **LEGITIMATE**.

The project was chosen to demonstrate how a simple and explainable cybersecurity system can detect common phishing patterns without using machine learning.

### Expected Outcome

The objective was to build a detector that:

1. Accepts email content as input.
2. Detects common phishing indicators.
3. Assigns a risk score.
4. Classifies the email as phishing or legitimate.
5. Displays the detected indicators.
6. Tests the detector using 5 phishing and 5 legitimate emails.
7. Reports correct classifications, false positives, false negatives, and accuracy.
---

## 2. Requirements

### Hardware

| Component | Qty | Purpose |
|---|---:|---|
| Computer/Laptop | 1 | Development and testing |
| Keyboard and Mouse | 1 | Input and development |

### Software
| Tool / Library | Version | Purpose |
|---|---|---|
| [Tool] | [v] | [Purpose] |

**Constraints:** [Budget / hardware / time / power / etc.]

| Tool / Library | Version | Purpose |
|---|---|---|
| HTML5 | - | Webpage structure |
| CSS3 | - | User interface and styling |
| JavaScript | ES6+ | Detection logic and evaluation |
| Visual Studio Code | Latest | Code editor |
| Git | Latest | Version control |
| GitHub | - | Repository and submission |
| Web Browser | Latest | Running and testing |

**Constraints:** The project is completely software-based and does not require additional hardware. The detector must work without machine learning.


---

## 3. Design

### System Overview

The detector follows a rule-based processing pipeline.

```text
Email Input
    |
    v
Convert and normalize text
    |
    v
Check phishing indicators
    |
    v
Calculate risk score
    |
    v
Compare score with threshold
    |
    +----------------------+
    |                      |
 Score >= 5             Score < 5
    |                      |
    v                      v
 PHISHING              LEGITIMATE
    |                      |
    +----------+-----------+
               |
               v
     Display result and
     detected indicators



![System Diagram](./docs/images/system-overview.png)

### Key Decisions
What did you choose, why, and what did you reject?
Rule-Based Detection
A rule-based approach was selected because the project requires a phishing detector without machine learning.
The main advantage is transparency. Every classification can be explained by showing which indicators were detected and how many points each indicator contributed.

Weighted Scoring
Different phishing indicators have different levels of importance.

Indicator	Score
Urgent or threatening language	+2
Request for sensitive information	+3
Account verification request	+2
Suspicious URL pattern	+2
URL using an IP address	+3
Potentially dangerous attachment	+2
Generic greeting	+1
Excessive exclamation marks	+1
Suspicious link request	+1


The classification threshold is:
Risk Score >= 5  -> PHISHING
Risk Score < 5   -> LEGITIMATE

A weighted system was selected instead of simple keyword matching because one word alone should not automatically classify an email as phishing.

---

## 4. Implementation

Explain the important hardware, firmware, software, algorithms, circuits, protocols, and calculations.

Link to relevant source files. Do not dump large code blocks here.

The project uses three main files:
- index.html - webpage structure and interface
- style.css - user interface styling
- script.js - detection rules, scoring, test dataset, and evaluation
Text Processing
The email is converted to lowercase before analysis so that the detector can identify patterns regardless of capitalization.
Defanged URLs such as:
hxxps://example[.]com/login

are normalized before URL analysis.

---

## 5. Demonstration

Cover **every assigned demonstration requirement**.

I need your requirement + need elegantly here, you could simply insert a youtube link for the recordings, No issues!

---
The project demonstration covers all assigned requirements.
Requirement 1: Test 5 Phishing Emails
Five phishing test emails were used.
They contain common phishing characteristics including:
- Account suspension threats
- Password requests
- Account verification requests
- Suspicious links
- Credential requests
- Urgent language
The test emails are identified as:
P1 Subject: Account Suspension Notice

Dear Customer,

Your email account is scheduled to be suspended.

If you did not request this action, cancel the request immediately.

Your account and email data may be lost if you do not respond.

Click the link below to cancel the suspension:

hxxps://example[.]com/cancel

Regards,
Mail Administrator
P2 Subject: Your Password Will Expire

Dear User,

Your password will expire in 2 days.

Click here to re-change your password immediately:

hxxps://example[.]com/password

Thank you,
IT Help Desk
P3Subject: Security Notice

Dear Customer,

Our security system has detected unusual activity
connected to your account.

You will be unable to access your account unless
you verify your account immediately.

CLICK HERE TO VALIDATE NOW

hxxps://example[.]com/verify

Failure to verify within 24 hours may result in
your account being restricted.

Mail Administrator
P4 Subject: Important PayPal Security Alert

Dear Client,

Your account was recently reviewed and flagged
because of potentially fraudulent transactions.

To avoid restrictions on your account,
please verify your information by logging in.

hxxps://example[.]com/login

Please verify your account immediately.

PayPal Security Team
P5Subject: Important Salary Notification

Hello,

You have an important message from the Human
Resources Department regarding your salary.

The document is available through the secure
company network.

Access the document here:

hxxps://example[.]com/document

Ensure your login credentials are correct
to avoid cancellation.

Regards,
Human Resources Department
Requirement 2: Test 5 Legitimate Emails
Five legitimate test emails were used.
They include:
- Project meeting notification
- Order shipping notification
- Technology newsletter
- Password change confirmation
- College workshop registration
The legitimate emails are identified as:
L1 Subject: Project Meeting Tomorrow

Hi Aman,

This is a reminder that our project meeting is scheduled
for tomorrow at 10 AM.

Please bring the project report and your presentation.

Regards,
Project Team
L2 Subject: Your Order Has Shipped

Hello Aman,

Your order has been shipped successfully.

You can track the package from your order page on our
website.

Thank you for shopping with us.

Regards,
Customer Support
L3 Subject: Monthly Technology Newsletter

Hello,

Here are this month's technology articles, announcements,
and company updates.

You can read them whenever convenient.

Regards,
Newsletter Team
L4 Subject: Password Change Confirmation

Hi Aman,

Your password was successfully changed.

If you made this change, no action is required.

If you did not make this change, please contact our
support team through the official website.

Regards,
Security Team
L5 Subject: Technical Workshop Registration

Dear Students,

Registration for the technical workshop is now open.

The workshop will be held on Friday at 2 PM in the
college seminar hall.

Please register through the college portal before Thursday.

Regards,
Event Team


The detector was tested against all 10 emails.
ID	Actual	Predicted	Result
P1	PHISHING	LEGITIMATE	❌ False Negative
P2	PHISHING	PHISHING	✅ Correct
P3	PHISHING	PHISHING	✅ Correct
P4	PHISHING	PHISHING	✅ Correct
P5	PHISHING	LEGITIMATE	❌ False Negative
L1	LEGITIMATE	LEGITIMATE	✅ Correct
L2	LEGITIMATE	LEGITIMATE	✅ Correct
L3	LEGITIMATE	LEGITIMATE	✅ Correct
L4	LEGITIMATE	LEGITIMATE	✅ Correct
L5	LEGITIMATE	LEGITIMATE	✅ Correct
Requirement 4: False Positives
A false positive occurs when a legitimate email is classified as phishing.
Actual: LEGITIMATE
Predicted: PHISHING
Number of false positives:
0
Requirement 5: False Negatives
A false negative occurs when a phishing email is classified as legitimate.
Actual: PHISHING
Predicted: LEGITIMATE
Number of false negatives:
2
The false negatives occurred for:
P1
P5
These examples did not reach the risk-score threshold of 5.
Requirement 6: Accuracy
The detector correctly classified 8 out of 10 emails.
Correct Classifications = 8
Total Emails = 10

Accuracy = (8 / 10) × 100

Accuracy = 80%

Final Test Results
Metric	Result
Total Emails	10
Correct Classifications	8
Incorrect Classifications	2
False Positives	0
False Negatives	2
Accuracy	80%

What the Detector Looks For
The detector looks for multiple indicators rather than relying on a single keyword.
For example, an email containing:


URGENT

Your account will be suspended.

Verify your account immediately.

Enter your password and OTP.

http://192.168.1.50/login

can receive points for:
- Urgent language
- Sensitive information request
- Account verification
- IP-address URL
- Suspicious URL pattern
This increases the overall risk score and can result in a phishing classification.

## 6. Final Result

### Working
Working
- Email content can be entered through the web interface.
- The detector analyzes the email using predefined rules.
- A weighted risk score is calculated.
- Emails are classified as phishing or legitimate.
- Detected phishing indicators are displayed.
- Five phishing emails are tested.
- Five legitimate emails are tested.
- Correct classifications are reported.
- False positives are calculated.
- False negatives are calculated.
- Overall accuracy is calculated.
- The detector works without machine learning.

### Known Issues
- The detector depends on manually defined rules.
- Different wording can cause a phishing email to be missed.
- Legitimate emails can contain words such as "password", "account", or "verify".
- The detector does not check sender reputation.
- The detector does not use external threat-intelligence databases.
- The detector does not inspect real attachments.
- The test dataset contains only 10 emails and is therefore too small to represent real-world email traffic.
The current evaluation produced two false negatives. This demonstrates a limitation of the rule-based approach rather than hiding incorrect classifications.

**Demo:** [Video Link]

![Final Build](./docs/images/final-build.jpg)

---

## 7. Limitations & Improvements

Limitations:
1. The detector uses manually defined rules.
2. New phishing techniques require new rules.
3. It does not analyze complete email headers.
4. It does not check sender/domain reputation.
5. It does not use live threat-intelligence services.
6. It does not inspect actual attachments.
7. The evaluation dataset contains only 10 emails.
8. Sophisticated phishing emails may avoid the predefined patterns.

**Next Steps:** [What you would improve with more time]
With additional development time, the detector could be improved by:
1. Adding sender-domain analysis.
2. Adding URL reputation checking.
3. Detecting more URL obfuscation techniques.
4. Analyzing email headers.
5. Expanding the test dataset.
6. Adding more phishing patterns.
7. Adding a larger collection of legitimate emails.
8. Comparing the rule-based approach with machine-learning methods as a future experiment.

---

## 8. Key Learnings

What did you actually learn from building and debugging this?

---This project provided practical experience with:
- Rule-based cybersecurity detection
- JavaScript string processing
- Regular expressions
- URL pattern detection
- Weighted scoring systems
- Classification thresholds
- False positives and false negatives
- Accuracy calculation
- Web development using HTML, CSS, and JavaScript
- Debugging rule-based systems
- Git and GitHub workflow
- Testing and documenting software
One important lesson was that phishing emails can use different wording to express the same malicious intent.
For example, a rule checking only:
account will be suspended
may fail to detect:
account is scheduled to be suspended

## 9. Repository Structure

aman-negi/
├── README.md
├── phishing-email-detector/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── docs/
    └── images/
        ├── system-overview.png
        └── final-build.png