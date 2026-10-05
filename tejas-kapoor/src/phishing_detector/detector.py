"""Rule-based phishing email detector (no machine learning).

Each indicator adds weighted points; total >= THRESHOLD means PHISHING.
"""
from email import message_from_string, policy
import re
from urllib.parse import urlparse

THRESHOLD = 5

# brand keyword -> domains that legitimately send for that brand
BRANDS = {
    "paypal": {"paypal.com"},
    "microsoft": {"microsoft.com", "office.com", "outlook.com", "microsoftonline.com"},
    "amazon": {"amazon.com", "amazon.in"},
    "google": {"google.com", "accounts.google.com", "gmail.com"},
    "dhl": {"dhl.com"},
    "hdfc": {"hdfcbank.com", "hdfcbank.net"},
    "github": {"github.com"},
}

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rb.gy"}
BAD_EXT = (".exe", ".scr", ".js", ".vbs", ".bat", ".html", ".htm", ".docm", ".xlsm", ".zip", ".iso")

URGENCY = ["urgent", "immediately", "within 24 hours", "act now", "final notice",
           "expires today", "right away", "asap", "last warning", "as soon as possible"]
THREATS = ["account will be suspended", "account has been suspended", "locked", "terminated",
           "legal action", "permanently closed", "unauthorized activity", "restricted"]
CREDENTIALS = ["verify your", "confirm your password", "update your password", "enter your password",
               "login details", "confirm your identity", "card number", "cvv", "otp", "pin",
               "social security", "re-enter your"]
LURES = ["you have won", "lottery", "claim your prize", "gift card", "wire transfer",
         "inheritance", "free iphone", "congratulations"]
GENERIC_GREETINGS = ["dear customer", "dear user", "dear client", "dear account holder",
                     "dear member", "valued customer"]

LINK_RE = re.compile(r'<a\s+href="([^"]+)"\s*>(.*?)</a>', re.I | re.S)
BARE_URL_RE = re.compile(r'https?://[^\s<>"]+', re.I)


def domain_of(addr_or_url):
    s = addr_or_url.strip().lower()
    if "@" in s and "//" not in s:
        s = s.split("@")[-1].strip(">").strip()
        return s
    return (urlparse(s if "//" in s else "//" + s).hostname or "")


def root(domain):
    parts = domain.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else domain


def normalize(domain):
    """Undo common look-alike tricks: paypa1 -> paypal, rn -> m, etc."""
    d = domain.lower().replace("rn", "m")
    return d.translate(str.maketrans("0135$", "oleas")).replace("-", "")


def lookalike_brand(domain):
    """Return brand if domain imitates it but is not an official domain."""
    r = root(domain)
    for brand, legit in BRANDS.items():
        if r in legit:
            return None
    n = normalize(domain)
    for brand in BRANDS:
        if brand in n:
            return brand
    return None


def analyze(email):
    hits = []  # (points, description)
    text = (email["subject"] + " " + email["body"]).lower()
    sender = domain_of(email["from"])

    def add(points, msg):
        hits.append((points, msg))

    # --- Sender checks ---
    brand = lookalike_brand(sender)
    if brand:
        add(4, f"Sender domain '{sender}' imitates '{brand}'")
    for b, legit in BRANDS.items():
        if b in email["from"].split("<")[0].lower() and root(sender) not in legit:
            add(3, f"Display name claims '{b}' but sends from '{sender}'")
            break
    else:
        # brand named in subject/body, sender is unrelated
        for b, legit in BRANDS.items():
            if b in text and root(sender) not in legit and not brand:
                add(2, f"Mentions '{b}' but sender domain is '{sender}'")
                break
    rt = email.get("reply_to")
    if rt and root(domain_of(rt)) != root(sender):
        add(2, f"Reply-To domain '{domain_of(rt)}' differs from sender")

    # --- Link checks ---
    links = LINK_RE.findall(email["body"])
    seen = {href for href, _ in links}
    for u in BARE_URL_RE.findall(LINK_RE.sub("", email["body"])):
        if u not in seen:
            links.append((u, u))
    for href, shown in links:
        host = domain_of(href)
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
            add(4, f"Link uses raw IP address: {href}")
        if host in SHORTENERS:
            add(2, f"URL shortener hides destination: {host}")
        if href.lower().startswith("http://"):
            add(1, f"Unencrypted (http) link: {host}")
        if "xn--" in host:
            add(3, f"Punycode (possible homograph) domain: {host}")
        if "@" in urlparse(href).netloc:
            add(3, "'@' in URL authority (obfuscation)")
        if host.count(".") >= 3:
            add(1, f"Excessive subdomains: {host}")
        lb = lookalike_brand(host)
        if lb:
            add(4, f"Link domain '{host}' imitates '{lb}'")
        shown_hosts = BARE_URL_RE.findall(shown) or re.findall(r"[\w.-]+\.(?:com|net|org|in|io)\b", shown.lower())
        for sh in shown_hosts:
            sh_host = domain_of(sh)
            if sh_host and root(sh_host) != root(host):
                add(4, f"Link text shows '{sh_host}' but goes to '{host}'")
                break

    # --- Content checks ---
    def count(words, haystack=None):
        h = text if haystack is None else haystack
        return [w for w in words if re.search(r"\b" + re.escape(w) + r"\b", h)]

    u = count(URGENCY)
    if u:
        add(min(3, 1 + len(u)), f"Urgency language: {', '.join(u[:3])}")
    t = count(THREATS)
    if t:
        add(2, f"Threat language: {', '.join(t[:3])}")
    warned = re.sub(r"\b(?:never|do not|don't|please do not)\s+(?:share|give|disclose|reveal)\b[^.!\n]*", " ", text)
    c = count(CREDENTIALS, warned)
    if c:
        add(3, f"Requests credentials/sensitive data: {', '.join(c[:3])}")
    l = count(LURES)
    if l:
        add(2, f"Lure/payment-scam wording: {', '.join(l[:3])}")
    g = [x for x in GENERIC_GREETINGS if x in text]
    if g:
        add(1, f"Generic greeting: '{g[0]}'")
    if len(re.findall(r"!", email["body"])) >= 3 or len(re.findall(r"\b[A-Z]{5,}\b", email["body"])) >= 3:
        add(1, "Excessive exclamation marks / ALL-CAPS")

    # --- Attachments ---
    for a in email.get("attachments", []):
        if a.lower().endswith(BAD_EXT):
            add(4, f"Risky attachment type: {a}")
        if re.search(r"\.(pdf|docx?|xlsx?)\.(exe|scr|js|zip)$", a.lower()):
            add(3, f"Double extension: {a}")

    score = sum(p for p, _ in hits)
    return score, ("PHISHING" if score >= THRESHOLD else "LEGITIMATE"), hits


def parse_raw(raw):
    """Turn a pasted raw email (headers + body) into the dict analyze() expects."""
    msg = message_from_string(raw, policy=policy.default)
    plain, html, atts = "", "", []
    for part in msg.walk():
        fn = part.get_filename()
        if fn:
            atts.append(fn)
        elif part.get_content_type() == "text/html":
            html += part.get_content()
        elif part.get_content_type() == "text/plain":
            plain += part.get_content()
    return {"from": str(msg["from"] or ""), "reply_to": str(msg["reply-to"] or ""),
            "subject": str(msg["subject"] or ""), "body": html or plain, "attachments": atts}


def evaluate(emails):
    """Classify labelled emails; return (per-email rows, confusion counts)."""
    names = {"tp": "correct", "tn": "correct", "fp": "false positive", "fn": "false negative"}
    rows, c = [], {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    for e in emails:
        score, verdict, hits = analyze(e)
        truth, pred = e["label"] == "PHISHING", verdict == "PHISHING"
        k = "tp" if truth and pred else "tn" if not truth and not pred else "fp" if pred else "fn"
        c[k] += 1
        rows.append({"name": e["name"], "from": e["from"], "subject": e["subject"], "truth": e["label"],
                     "verdict": verdict, "score": score, "result": names[k],
                     "indicators": [{"points": p, "text": m} for p, m in hits]})
    c["accuracy"] = (c["tp"] + c["tn"]) / len(emails)
    return rows, c
