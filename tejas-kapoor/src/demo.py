"""Command-line demonstration: python demo.py"""
from phishing_detector import EMAILS, THRESHOLD, evaluate

rows, c = evaluate(EMAILS)
print(f"Threshold: score >= {THRESHOLD} => PHISHING\n" + "=" * 72)
for r in rows:
    print(f"{r['name']:<34} truth={r['truth']:<9} pred={r['verdict']:<10} score={r['score']:<3} {r['result'].upper()}")
    for i in r["indicators"]:
        print(f"    +{i['points']}  {i['text']}")
print("=" * 72)
print(f"Correct: {c['tp'] + c['tn']}/{len(rows)}   False positives: {c['fp']}   False negatives: {c['fn']}")
