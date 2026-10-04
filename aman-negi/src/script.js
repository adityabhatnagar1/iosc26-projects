const indicators = [
    {
        name: "Urgent or threatening language",
        score: 2,
        patterns: [
            "urgent",
            "immediately",
            "act now",
            "last warning",
            "account will be suspended",
            "account is scheduled to be suspended",
            "within 24 hours",
            "failure to verify"
        ]
    },
    {
        name: "Request for sensitive information",
        score: 3,
        patterns: [
            "password",
            "otp",
            "credit card",
            "bank account",
            "login credentials",
            "security code"
        ]
    },
    {
        name: "Account verification request",
        score: 2,
        patterns: [
            "verify your account",
            "verify your identity",
            "confirm your account",
            "update your account",
            "validate your account"
        ]
    },
    {
        name: "Suspicious URL pattern",
        score: 2,
        patterns: [
            "login",
            "verify",
            "secure",
            "update",
            "account",
            "password",
            "confirm"
        ]
    },
    {
        name: "Dangerous attachment",
        score: 2,
        patterns: [
            ".exe",
            ".scr",
            ".bat",
            ".cmd",
            ".js",
            ".zip",
            ".msi"
        ]
    }
];

function normalizeEmail(text) {
    return text
        .toLowerCase()
        .replace(/hxxps:\/\//g, "https://")
        .replace(/hxxp:\/\//g, "http://")
        .replace(/\[\.\]/g, ".");
}

function detectPhishing(email) {
    const text = normalizeEmail(email);
    let score = 0;
    const foundIndicators = [];

    for (const indicator of indicators) {
        let found = false;

        for (const pattern of indicator.patterns) {
            if (text.includes(pattern)) {
                found = true;
                break;
            }
        }

        if (found) {
            score += indicator.score;
            foundIndicators.push({
                name: indicator.name,
                score: indicator.score
            });
        }
    }

    const urlPattern = /https?:\/\/[^\s]+/g;
    const urls = text.match(urlPattern) || [];

    if (urls.length > 0) {
        const suspiciousUrl = urls.some(url =>
            /login|verify|secure|update|account|password|confirm/.test(url)
        );

        if (
            suspiciousUrl &&
            !foundIndicators.some(
                item => item.name === "Suspicious URL pattern"
            )
        ) {
            score += 2;
            foundIndicators.push({
                name: "Suspicious URL pattern",
                score: 2
            });
        }

        const ipUrl = urls.some(url =>
            /https?:\/\/\d{1,3}(\.\d{1,3}){3}/.test(url)
        );

        if (ipUrl) {
            score += 3;
            foundIndicators.push({
                name: "URL using an IP address",
                score: 3
            });
        }
    }

    if (/dear (customer|user|client)\b/.test(text)) {
        score += 1;
        foundIndicators.push({
            name: "Generic greeting",
            score: 1
        });
    }

    if ((email.match(/!/g) || []).length >= 3) {
        score += 1;
        foundIndicators.push({
            name: "Excessive exclamation marks",
            score: 1
        });
    }

    if (
        /click (here|the link)|click here|access the document here/.test(
            text
        )
    ) {
        score += 1;
        foundIndicators.push({
            name: "Suspicious link request",
            score: 1
        });
    }

    return {
        classification: score >= 5 ? "PHISHING" : "LEGITIMATE",
        score,
        indicators: foundIndicators
    };
}

function checkEmail() {
    const email = document.getElementById("emailInput").value.trim();
    const result = document.getElementById("result");

    if (!email) {
        result.innerHTML = "<p>Please enter an email.</p>";
        return;
    }

    const analysis = detectPhishing(email);

    let html = `
        <h2>${analysis.classification}</h2>
        <p>Risk Score: ${analysis.score}</p>
    `;

    if (analysis.indicators.length > 0) {
        html += `<div class="indicators"><h3>Detected Indicators</h3><ul>`;

        analysis.indicators.forEach(indicator => {
            html += `<li>${indicator.name} (+${indicator.score})</li>`;
        });

        html += `</ul></div>`;
    } else {
        html += `<p>No phishing indicators detected.</p>`;
    }

    result.innerHTML = html;
}

const testDataset = [
    {
        id: "P1",
        actual: "PHISHING",
        email: `Subject: Account Suspension Notice

Dear Customer,

Your email account is scheduled to be suspended.

If you did not request this action,
cancel the request immediately.

Your account and email data may be lost
if you do not respond.

Click the link below to cancel the suspension:

hxxps://example[.]com/cancel

Regards,
Mail Administrator`
    },
    {
        id: "P2",
        actual: "PHISHING",
        email: `Subject: Your Password Will Expire

Dear User,

Your password will expire in 2 days.

Click here to re-change your password
immediately:

hxxps://example[.]com/password

Thank you,
IT Help Desk`
    },
    {
        id: "P3",
        actual: "PHISHING",
        email: `Subject: Security Notice

Dear Customer,

Our security system has detected unusual
activity connected to your account.

You will be unable to access your account
unless you verify your account immediately.

CLICK HERE TO VALIDATE NOW

hxxps://example[.]com/verify

Failure to verify within 24 hours may result
in your account being restricted.

Mail Administrator`
    },
    {
        id: "P4",
        actual: "PHISHING",
        email: `Subject: Important PayPal Security Alert

Dear Client,

Your account was recently reviewed and flagged
because of potentially fraudulent transactions.

To avoid restrictions on your account,
please verify your information by logging in.

hxxps://example[.]com/login

Please verify your account immediately.

PayPal Security Team`
    },
    {
        id: "P5",
        actual: "PHISHING",
        email: `Subject: Important Salary Notification

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
Human Resources Department`
    },
    {
        id: "L1",
        actual: "LEGITIMATE",
        email: `Subject: Project Meeting Tomorrow

Hi Aman,

This is a reminder that our project meeting is scheduled
for tomorrow at 10 AM.

Please bring the project report and your presentation.

Regards,
Project Team`
    },
    {
        id: "L2",
        actual: "LEGITIMATE",
        email: `Subject: Your Order Has Shipped

Hello Aman,

Your order has been shipped successfully.

You can track the package from your order page on our
website.

Thank you for shopping with us.

Regards,
Customer Support`
    },
    {
        id: "L3",
        actual: "LEGITIMATE",
        email: `Subject: Monthly Technology Newsletter

Hello,

Here are this month's technology articles, announcements,
and company updates.

You can read them whenever convenient.

Regards,
Newsletter Team`
    },
    {
        id: "L4",
        actual: "LEGITIMATE",
        email: `Subject: Password Change Confirmation

Hi Aman,

Your password was successfully changed.

If you made this change, no action is required.

If you did not make this change, please contact our
support team through the official website.

Regards,
Security Team`
    },
    {
        id: "L5",
        actual: "LEGITIMATE",
        email: `Subject: Technical Workshop Registration

Dear Students,

Registration for the technical workshop is now open.

The workshop will be held on Friday at 2 PM in the
college seminar hall.

Please register through the college portal before Thursday.

Regards,
Event Team`
    }
];

function runTestDataset() {
    const testResults = document.getElementById("testResults");

    let correct = 0;
    let falsePositives = 0;
    let falseNegatives = 0;

    let rows = "";

    testDataset.forEach(test => {
        const result = detectPhishing(test.email);
        const predicted = result.classification;

        if (predicted === test.actual) {
            correct++;
        } else if (
            test.actual === "LEGITIMATE" &&
            predicted === "PHISHING"
        ) {
            falsePositives++;
        } else if (
            test.actual === "PHISHING" &&
            predicted === "LEGITIMATE"
        ) {
            falseNegatives++;
        }

        const isCorrect = predicted === test.actual;

        rows += `
            <tr>
                <td>${test.id}</td>
                <td>${test.actual}</td>
                <td>${predicted}</td>
                <td>${isCorrect ? "Correct" : "Incorrect"}</td>
                <td>${result.score}</td>
            </tr>
        `;
    });

    const total = testDataset.length;
    const incorrect = total - correct;
    const accuracy = ((correct / total) * 100).toFixed(2);

    testResults.innerHTML = `
        <h2>Test Results</h2>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Actual</th>
                    <th>Predicted</th>
                    <th>Result</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>

        <div class="summary">
            <p>Total Emails: ${total}</p>
            <p>Correct Classifications: ${correct}</p>
            <p>Incorrect Classifications: ${incorrect}</p>
            <p>False Positives: ${falsePositives}</p>
            <p>False Negatives: ${falseNegatives}</p>
            <p>Accuracy: ${accuracy}%</p>
        </div>
    `;
}