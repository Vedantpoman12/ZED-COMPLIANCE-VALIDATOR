# Document Verification Status Guide

## 🚦 Status Messages Explained

### ✅ **Green Statuses (VERIFIED)**

#### "STATUS: Verified (Authentic Document)"
- **Meaning:** Document is authentic AND has valid format
- **When shown:** 
  - Authenticity check passed (matches your real documents)
  - PAN number format is correct
- **Action:** ✓ Document is safe to accept

#### "STATUS: Likely Authentic"  
- **Meaning:** Document appears genuine based on ML comparison
- **When shown:**
  - Authenticity check passed
  - May not have detectable ID numbers but structure looks real
- **Action:** ✓ Probably safe, check manually if critical

#### "STATUS: Verified (No Issues Found)"
- **Meaning:** Valid format detected (no authenticity check)
- **When shown:**
  - PAN number is correctly formatted
  - No authenticity model trained yet
- **Action:** ✓ Format is correct, but can't verify authenticity

#### "STATUS: Processed Successfully"
- **Meaning:** Document uploaded and text extracted
- **When shown:** 
  - Non-PAN/Aadhaar documents
  - Or documents without authenticity training
- **Action:** ℹ️ Basic verification only

---

### ⚠️ **Yellow Statuses (MINOR NOTES)**

#### "STATUS: Verified with Minor Notes"
- **Meaning:** Looks like a PAN card but ID number unclear
- **When shown:**
  - Document identified as PAN
  - PAN number format not detected (poor quality/altered)
- **Action:** ⚠️ Review manually, might be low quality or fake

---

### 🔴 **Red Statuses (REVIEW REQUIRED)**

#### "STATUS: SUSPICIOUS - Possible Fake Document" ⚠️
- **Meaning:** Document likely FAKE or ALTERED
- **When shown:**
  - Authenticity check FAILED
  - Document differs significantly from real documents
  - Low confidence score
- **Action:** 🚫 **DO NOT ACCEPT** - Probable fake!

#### "STATUS: Requires Further Review"
- **Meaning:** Can't extract text to verify
- **When shown:**
  - Image quality too low
  - Blank document
  - Corrupted file
- **Action:** 📤 Request better quality upload

---

## 🎯 Priority Order

The system checks in this order:

1. **FIRST:** Authenticity (is it fake?)
   - If FAKE → Show "SUSPICIOUS" status
   - If AUTHENTIC → Show "Verified" status

2. **SECOND:** Format validation (PAN number, etc.)
   - Valid format → "No Issues Found"
   - Invalid format → "Minor Notes"

3. **THIRD:** Text extraction
   - No text → "Requires Further Review"

---

## 📊 Confidence Scores

- **≥ 60%** → Authentic (Green)
- **< 60%** → Suspicious/Fake (Red)

The confidence shows how similar the document is to your trained authentic documents.

---

## 💡 Tips

### To improve accuracy:
1. Train on multiple real documents (more = better)
2. Upload high-quality scans (300 DPI+)
3. Ensure documents are well-lit and not blurry

### If you see "Requires Further Review":
- Re-scan the document at higher quality
- Check if PDF is image-based (not text-based)
- Convert PDF to JPG/PNG and retry
