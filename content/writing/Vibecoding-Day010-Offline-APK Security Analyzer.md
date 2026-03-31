---
title: "The APK Analyzer That Runs on Your Machine and Tells No One"
date: 2026-03-31
tags: ["Security", "Android", "Flask", "Python", "VibeCoding"]
---

### Building an Offline APK Security Analyzer in Flask

*Project #10 of the 100 Vibe Coding Projects challenge*

---

I've been doing APK security analysis manually for years — pulling the file, running jadx, grepping through decompiled source, eyeballing the manifest. It works, but it's slow and the output lives in a terminal window that disappears the moment you close it.

This week's project: wrap that entire methodology into a local web tool. Upload an APK, get a structured risk report in your browser. No internet required, nothing stored, APK deleted the moment analysis completes.

Here's how it was built and what I learned.

---

### Why Offline?

The obvious question when you hear "web tool for APK analysis" is: why not just use MobSF or one of the online scanners?

Two reasons. First, the APKs worth analyzing carefully are often the ones you'd least want to upload to a third-party server — financial apps, enterprise apps, apps handling sensitive user data. Running analysis locally eliminates that question entirely.

Second, building it yourself means you control the logic. Every SDK detection rule, every secret pattern, every risk classification — you wrote it, you understand it, you can explain it. That matters when you're presenting findings to someone.

---

### The Architecture

The tool is deliberately simple. Flask handles the file upload and routing. androguard does the heavy lifting on the APK binary. Jinja2 renders the report. No database, no queue, no JavaScript framework.

```
Browser → Flask → androguard/zipfile → Jinja2 report
```

Five analysis modules run sequentially on the uploaded APK:

1. **Manifest parser** — package metadata, permissions, exported components
2. **Secret scanner** — regex patterns over text resources
3. **SDK fingerprinter** — DEX class namespace matching
4. **Crypto analyzer** — control and weakness detection
5. **Network security config parser** — pinning, cleartext, CA trust

---

### The Interesting Technical Problem: DEX Class Extraction

The first version of the SDK fingerprinter searched the APK's ZIP contents for file paths like `smali/com/dynatrace/...`. That works if you have a smali-format APK, but standard Play Store APKs don't contain smali files — the code is compiled DEX.

The fix was using androguard to parse the DEX bytecode directly and extract class names:

```python
from androguard.misc import AnalyzeAPK

def get_dex_classes(apk_path):
    try:
        a, d, dx = AnalyzeAPK(apk_path)
        return set(
            c.name.lstrip('L').replace(';', '').replace('.', '/')
            for c in dx.get_classes()
        )
    except Exception as e:
        print(f"[DEX] {e}")
        return set()
```

The class names come out of DEX in JVM descriptor format — `Lcom/dynatrace/android/agent/Dynatrace;` — so we strip the leading `L` and trailing `;` to get `com/dynatrace/android/agent/Dynatrace`, which can then be prefix-matched against our SDK map.

This function gets called once and the result is shared across both the SDK fingerprinter and the crypto analyzer, avoiding parsing the DEX twice.

---

### SDK Detection: Curating the Map

The SDK map is the heart of the tool. Each entry maps a class namespace prefix to a name, category, risk level, and a specific security note:

```python
SDK_MAP = {
    'com/dynatrace': (
        'Dynatrace',
        'SESSION REPLAY',
        'HIGH',
        'Full session replay capable — verify DataCollectionLevel=PERFORMANCE'
    ),
    'com/adobe/marketing/mobile': (
        'Adobe Experience Platform',
        'TRACKING',
        'HIGH',
        'Full behavioral profiling — Analytics, Target, Identity, Audience'
    ),
    'androidx/biometric': (
        'AndroidX Biometric',
        'AUTH',
        'GOOD',
        'Hardware-backed biometric authentication'
    ),
    # ... 30+ more
}
```

The risk classifications aren't arbitrary. Dynatrace is HIGH because its default `DataCollectionLevel` is `USER_BEHAVIOR`, which enables full session replay. On a banking app, that means account balances and transaction history may be recorded. The note tells you exactly what to verify.

Security controls get a `GOOD` classification — the tool distinguishes between "this SDK sends data to a third party" and "this SDK provides a security control that should be present."

---

### The Network Security Config Check

The most actionable finding the tool surfaces is expired certificate pinning. Android's `NetworkSecurityConfig` supports a `pin-set` with an optional `expiration` attribute:

```xml
<pin-set expiration="2025-12-31">
    <pin digest="SHA-256">HASH=</pin>
</pin-set>
```

When the expiration date passes, Android silently falls back to trusting all system CA certificates. The pinning doesn't fail loudly — it just stops working. The tool checks this explicitly:

```python
exp = re.search(r'expiration="([^"]+)"', xml)
if exp:
    if datetime.strptime(exp.group(1), '%Y-%m-%d') < datetime.now():
        # Certificate pinning silently disabled
        findings.append({'status': 'FAIL', 'text': f'Pin expiration LAPSED: {exp_date}', ...})
```

This is a finding I've seen in real-world production apps. It's a five-minute fix once identified — remove the expiration attribute or update the date — but it's invisible unless you're specifically looking for it.

---

### Secret Scanning: Text Resources Only

The secrets scanner searches all text-format files inside the APK ZIP — XML resources, JSON configs, JS bundles, properties files. It won't find secrets compiled into DEX bytecode (you need JADX for that), but it catches a surprising amount:

- Firebase API keys in `google-services.json`  
- Staging URLs left in `strings.xml`
- Internal IP addresses in config files
- Razorpay/Stripe live keys in resource files
- Dynatrace beacon URLs that reveal your monitoring infrastructure

The tool is honest about this limitation — it tells you in the report that DEX bytecode requires JADX for full coverage.

---

### The Flask Routing

The upload route is straightforward. The file gets saved to a temp location, analysis runs, the file gets deleted in a `finally` block so it's gone whether analysis succeeds or fails:

```python
@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['apk_file']
    apk_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(apk_path)
    try:
        results = run_analysis(apk_path)
    except Exception as e:
        flash(f'Analysis failed: {str(e)}')
        return redirect(url_for('index'))
    finally:
        if os.path.exists(apk_path):
            os.remove(apk_path)
    return render_template('report.html', r=results)
```

The 150MB upload limit handles most APKs. Large apps with multiple split APKs may need the base APK pulled separately with `adb pull`.

---

### Risk Scoring

The report generates a letter grade (A–F) based on finding counts:

```
score = 100 - (critical × 20) - (high × 10) - (medium × 3)
```

An app with no critical or high findings gets an A regardless of score. The grade is a conversation starter, not a compliance verdict — the real value is in the specific findings.

---

### What I Learned Building This

**androguard's API changed significantly between v3 and v4.** Most tutorials and Stack Overflow answers reference the v3 API (`APK`, `DalvikVMFormat`, `Analysis`). In v4, the import paths moved and the class iteration API changed. The v4 way is `AnalyzeAPK()` returning a tuple of `(APK, list[DEX], Analysis)`.

**Binary AXML is genuinely annoying.** Android's compiled binary XML format (AXML) is what's actually inside the APK's `AndroidManifest.xml`. Parsing it correctly from scratch requires implementing the full chunk format — string pool, resource map, element nodes. androguard handles this, but only if you feed it a properly signed APK. The fallback to regex over the raw binary catches basic package names and permissions when the parser fails.

**Silent failures are the enemy of security tools.** Early versions of the SDK fingerprinter swallowed all exceptions quietly. The DEX extraction would fail, `dex_classes` would be empty, and the report would show zero SDKs with no indication anything went wrong. Adding explicit `print(f"[DEX] {e}")` statements made debugging immediate.

**Flask's template discovery is strict about working directory.** `render_template('index.html')` looks for `templates/` relative to where the Flask app is instantiated, which is the directory you ran `python3 app.py` from. Running the script from a different directory breaks template discovery silently.

---

### Running It

```bash
git clone https://github.com/yourusername/apk-security-analyzer
cd apk-security-analyzer
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 app.py
# Open http://localhost:5000
```

Grab any APK from APKMirror, upload it, and see what's in it.

---

### What's Next

The natural next step is adding JADX integration — run the decompiler automatically and grep the output for the high-value patterns (onReceivedSslError, DataCollectionLevel, trackAction calls). That would close the gap between what static resource scanning catches and what method-level analysis reveals.

A diff mode would also be useful — upload two versions of the same APK and see what SDKs were added or removed between releases. That's how you catch a marketing team quietly adding a new tracking SDK between app updates.

---

### Code 
[Access it at github.com](https://github.com/mr-dinesh/Offline-APK-Analyzer)  
[Part of the 100 Vibe Coding Projects series] (https://mrdee.in)
