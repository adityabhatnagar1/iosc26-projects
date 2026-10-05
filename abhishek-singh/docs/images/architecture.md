# System Architecture & Privacy Model

## k-Anonymity Sequence Protocol

1. **Client interface:** The user supplies `P` (the plaintext password).
2. **Local hashing:** The client computes `H = SHA1(P)` (40 hex characters).
3. **Partitioning:**
   - `H_prefix = H[0:5]` (5 hex characters = 20 bits)
   - `H_suffix = H[5:40]` (35 hex characters = 140 bits)
4. **Network request:** The client sends `GET https://api.pwnedpasswords.com/range/<H_prefix>`.
5. **Server response:** HIBP returns every hash suffix in its dataset that shares `H_prefix`, one `SUFFIX:COUNT` pair per line.
6. **Local match:** The client searches the response for `H_suffix` and reads the exposure count. If it is absent, the password was not found in the dataset.

```text
Client                                          HIBP API
  |  P --SHA1--> H = <5-char prefix><35-char suffix>  |
  |--------- GET /range/<prefix> ------------------>|
  |<-------- ~500-1000 lines "SUFFIX:COUNT" --------|
  |  search for own 35-char suffix locally          |
```

## Local Analysis Pipeline

| Stage | Method | Output |
|---|---|---|
| Normalization | Lowercase, then reverse leetspeak substitutions | Normalized string used for keyword matching |
| Entropy | Shannon entropy over symbol frequencies, times length | Bits of entropy |
| Pattern rules | Regex table: sequences, keyboard walks, repeats, keywords, years | List of findings |
| Length check | Flag passwords shorter than 12 characters | Short-length finding |

## Rating Logic

| Rating | Condition |
|---|---|
| `CRITICAL / WEAK` | Found in a breach, **or** entropy < 35 bits, **or** length < 12 |
| `FAIR / MODERATE` | Entropy < 60 bits, **or** at least one pattern found |
| `STRONG` | None of the above |

## Security Proof & Privacy Guarantees

- **Mathematical privacy:** A SHA-1 hash holds 160 bits. Sending 20 bits (5 hex digits) leaves 140 bits that never leave the client.
- **Bucket size:** An average 5-hex range returns roughly 500-1,000 suffixes, so the server cannot tell which one, if any, the client is looking for.
- **No full hash on the wire:** Only the 5-character prefix is transmitted, over HTTPS.
- **Memory handling:** The plaintext password is kept in memory during execution and is not written to files by this tool.
- **Caveat:** A password passed on the command line (`--password`) may be stored in the shell's history by the shell itself, outside this tool's control.

## Failure Handling

| Condition | Behavior |
|---|---|
| Network error or timeout (3 s) | Breach status reported as unverified; local analysis still shown |
| Non-200 HTTP status | Same as above |
| Suffix not in response | Reported as zero known exposures |
