# Getting Test Medical Documents

## 🏥 Free Medical/Clinical Documents for Testing

### **Option 1: Sample Clinical Trial Documents** (Recommended)

**ClinicalTrials.gov** - Free public clinical trial documents

```bash
# Download sample clinical trial PDFs
mkdir -p test_documents
cd test_documents

# Example: Download from ClinicalTrials.gov
# Visit: https://clinicaltrials.gov/
# Search for any trial
# Download the "Study Protocol" PDF
```

**Direct Examples:**
1. Visit: https://clinicaltrials.gov/ct2/show/NCT04280705
2. Click "Study Documents"
3. Download "Study Protocol" or "Statistical Analysis Plan"

---

### **Option 2: PubMed Central Open Access**

Free full-text medical articles in PDF format

```bash
# Visit PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/

# Search for: "clinical trial" OR "randomized controlled trial"
# Filter by: "Free full text"
# Download PDF
```

**Example Articles:**
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7739050/pdf/
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8262656/pdf/

---

### **Option 3: HuggingFace Datasets**

Medical datasets with documents

```python
# Install datasets library
pip install datasets

# Load medical QA dataset
from datasets import load_dataset

# PubMedQA dataset
dataset = load_dataset("pubmed_qa", "pqa_labeled")

# MedQA dataset  
dataset = load_dataset("bigbio/med_qa")

# Clinical trials dataset
dataset = load_dataset("trialstreamer/trialstreamer")
```

---

### **Option 4: Sample Documents Included**

I'll create sample medical documents for you:

```bash
# Create test documents directory
mkdir -p test_documents
```

**Sample 1: Clinical Trial Summary**
```
Title: Phase III Study of Drug X in Hypertension
Primary Endpoint: Reduction in systolic blood pressure
Secondary Endpoints: Safety, tolerability
Inclusion Criteria: Adults 18-65 with hypertension
Dosing: 10mg daily for 12 weeks
Common Side Effects: Headache (15%), dizziness (8%), fatigue (5%)
```

**Sample 2: Medical Research Paper**
```
Abstract: This randomized controlled trial evaluated...
Methods: 500 patients were enrolled...
Results: Significant improvement in primary endpoint (p<0.001)
Conclusion: Drug X demonstrated efficacy and safety...
```

---

## 📥 Quick Download Script

```bash
#!/bin/bash

# Create test documents directory
mkdir -p test_documents
cd test_documents

# Download sample medical PDFs from PubMed Central
echo "Downloading sample medical documents..."

# Example 1: COVID-19 Clinical Trial
curl -o "covid19_trial.pdf" \
  "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7739050/pdf/main.pdf"

# Example 2: Diabetes Treatment Study
curl -o "diabetes_study.pdf" \
  "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8262656/pdf/main.pdf"

# Example 3: Cardiovascular Research
curl -o "cardio_research.pdf" \
  "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7923107/pdf/main.pdf"

echo "✅ Downloaded 3 sample medical documents"
ls -lh *.pdf
```

---

## 🧪 Test Document Recommendations

**For Interview Demo:**

1. **Short Document** (2-3 pages)
   - Quick processing
   - Easy to explain
   - Clear results

2. **Clinical Trial Protocol**
   - Shows medical domain
   - Has clear sections (endpoints, dosing, side effects)
   - Professional appearance

3. **Research Abstract**
   - Concise
   - Well-structured
   - Good for Q&A demo

---

## 📝 Creating Your Own Test Document

**Simple Test PDF:**

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_test_pdf():
    c = canvas.Canvas("test_clinical_trial.pdf", pagesize=letter)
    
    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Clinical Trial: Drug X for Hypertension")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "Primary Endpoint:")
    c.drawString(120, 700, "• Reduction in systolic blood pressure by ≥10 mmHg")
    
    c.drawString(100, 670, "Secondary Endpoints:")
    c.drawString(120, 650, "• Diastolic blood pressure reduction")
    c.drawString(120, 630, "• Safety and tolerability")
    
    c.drawString(100, 600, "Dosing Schedule:")
    c.drawString(120, 580, "• 10mg once daily for 12 weeks")
    c.drawString(120, 560, "• Taken with or without food")
    
    c.drawString(100, 530, "Common Side Effects:")
    c.drawString(120, 510, "• Headache (15% of patients)")
    c.drawString(120, 490, "• Dizziness (8% of patients)")
    c.drawString(120, 470, "• Fatigue (5% of patients)")
    
    c.save()
    print("✅ Created test_clinical_trial.pdf")

# Run
create_test_pdf()
```

---

## 🎯 Recommended for Your Demo

**Best Option**: Download from PubMed Central

1. Visit: https://www.ncbi.nlm.nih.gov/pmc/
2. Search: "randomized controlled trial"
3. Filter: "Free full text"
4. Pick any recent article
5. Download PDF
6. Upload to your app!

**Why?**
- ✅ Real medical content
- ✅ Professional appearance
- ✅ Publicly available
- ✅ No copyright issues
- ✅ Perfect for demo

---

## 📦 I'll Create Sample Documents

Let me create 2 sample PDFs for you right now...
