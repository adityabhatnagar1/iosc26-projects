import unittest
from phishing_detector import EMAILS, analyze, evaluate, parse_raw


class DetectorTests(unittest.TestCase):
    def test_demo_set_classified_correctly(self):
        rows, c = evaluate(EMAILS)
        self.assertEqual((c["fp"], c["fn"]), (0, 0), [r for r in rows if r["result"] != "correct"])

    def test_whole_word_matching(self):  # "blocked" must not trigger "locked"
        e = {"from": "a@x.org", "subject": "hi", "body": "We blocked a request."}
        self.assertEqual(analyze(e)[0], 0)

    def test_security_warning_not_credential_request(self):
        e = {"from": "a@x.org", "subject": "hi", "body": "Never share your OTP with anyone."}
        self.assertEqual(analyze(e)[0], 0)

    def test_lookalike_domain(self):
        e = {"from": "Bank <a@paypa1.com>", "subject": "hi", "body": "hello"}
        score, _, hits = analyze(e)
        self.assertEqual(score, 4)  # fires alone, but needs a second signal to cross the threshold
        self.assertTrue(any("imitates 'paypal'" in m for _, m in hits))

    def test_parse_raw(self):
        d = parse_raw("From: A <a@b.com>\nReply-To: c@d.com\nSubject: Hi\n\nBody text")
        self.assertEqual((d["subject"], d["reply_to"]), ("Hi", "c@d.com"))
        self.assertIn("Body text", d["body"])


if __name__ == "__main__":
    unittest.main()
