#!/usr/bin/env python3
"""
Create sample medical PDFs for testing
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pathlib import Path

def create_clinical_trial_pdf():
    """Create a clinical trial protocol PDF"""
    
    docs_dir = Path("test_documents")
    docs_dir.mkdir(exist_ok=True)
    
    filename = docs_dir / "clinical_trial_hypertension.pdf"
    
    c = canvas.Canvas(str(filename), pagesize=letter)
    width, height = letter
    y = height - inch
    
    # Page 1
    c.setFont("Helvetica-Bold", 18)
    c.drawString(inch, y, "Phase III Clinical Trial Protocol")
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Drug X for Treatment of Essential Hypertension")
    y -= 0.5 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Study Overview")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    lines = [
        "This is a randomized, double-blind, placebo-controlled study to evaluate",
        "the efficacy and safety of Drug X in patients with essential hypertension.",
        "",
        "Study Duration: 12 weeks",
        "Target Enrollment: 500 patients",
        "Study Sites: 25 centers across the United States",
    ]
    
    for line in lines:
        c.drawString(inch + 0.2*inch, y, line)
        y -= 0.2 * inch
    
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Primary Endpoint")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    c.drawString(inch + 0.2*inch, y, "• Reduction in systolic blood pressure by ≥10 mmHg from baseline at Week 12")
    y -= 0.4 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Secondary Endpoints")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    endpoints = [
        "• Reduction in diastolic blood pressure",
        "• Proportion of patients achieving blood pressure control (<140/90 mmHg)",
        "• Safety and tolerability assessment",
        "• Quality of life measures using SF-36 questionnaire"
    ]
    
    for endpoint in endpoints:
        c.drawString(inch + 0.2*inch, y, endpoint)
        y -= 0.2 * inch
    
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Dosing Schedule")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    dosing = [
        "• Drug X: 10mg once daily, taken in the morning",
        "• Administration: Oral tablet with or without food",
        "• Duration: 12 weeks of treatment",
        "• Follow-up: 4 weeks post-treatment"
    ]
    
    for dose in dosing:
        c.drawString(inch + 0.2*inch, y, dose)
        y -= 0.2 * inch
    
    # Page 2
    c.showPage()
    y = height - inch
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Safety and Adverse Events")
    y -= 0.4 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Common Side Effects")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    side_effects = [
        "Based on previous Phase II studies, the following adverse events were observed:",
        "",
        "• Headache: 15% of patients (mild to moderate intensity)",
        "• Dizziness: 8% of patients (usually transient, resolved within 2 weeks)",
        "• Fatigue: 5% of patients",
        "• Nausea: 3% of patients",
        "• Dry mouth: 2% of patients",
        "",
        "Serious adverse events were rare (<1%) and included hypotension requiring",
        "dose adjustment in 0.5% of patients."
    ]
    
    for effect in side_effects:
        c.drawString(inch + 0.2*inch, y, effect)
        y -= 0.2 * inch
    
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Patient Eligibility Criteria")
    y -= 0.25 * inch
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(inch + 0.2*inch, y, "Inclusion Criteria:")
    y -= 0.2 * inch
    
    c.setFont("Helvetica", 11)
    inclusion = [
        "• Age 18-65 years",
        "• Diagnosed with essential hypertension",
        "• Systolic blood pressure 140-180 mmHg at screening",
        "• Willing to provide written informed consent",
        "• Able to comply with study procedures and follow-up visits"
    ]
    
    for criteria in inclusion:
        c.drawString(inch + 0.4*inch, y, criteria)
        y -= 0.2 * inch
    
    y -= 0.2 * inch
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(inch + 0.2*inch, y, "Exclusion Criteria:")
    y -= 0.2 * inch
    
    c.setFont("Helvetica", 11)
    exclusion = [
        "• Secondary hypertension",
        "• Severe renal impairment (eGFR <30 mL/min)",
        "• Severe hepatic impairment (Child-Pugh Class C)",
        "• Recent cardiovascular event (within 6 months)",
        "• Pregnancy or breastfeeding",
        "• Known hypersensitivity to study drug or excipients"
    ]
    
    for criteria in exclusion:
        c.drawString(inch + 0.4*inch, y, criteria)
        y -= 0.2 * inch
    
    c.save()
    print(f"✅ Created: {filename}")
    return filename


def create_diabetes_study_pdf():
    """Create a diabetes treatment study PDF"""
    
    docs_dir = Path("test_documents")
    filename = docs_dir / "diabetes_treatment_study.pdf"
    
    c = canvas.Canvas(str(filename), pagesize=letter)
    width, height = letter
    y = height - inch
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(inch, y, "Randomized Controlled Trial")
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Novel Insulin Therapy for Type 2 Diabetes")
    y -= 0.5 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Abstract")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    abstract = [
        "Background: Type 2 diabetes mellitus affects millions worldwide. This study",
        "evaluates a novel long-acting insulin formulation.",
        "",
        "Methods: 300 patients with inadequately controlled type 2 diabetes were",
        "randomized to receive either the novel insulin or standard therapy.",
        "",
        "Results: The novel insulin demonstrated superior glycemic control with",
        "HbA1c reduction of 1.5% vs 0.8% in the control group (p<0.001).",
    ]
    
    for line in abstract:
        c.drawString(inch + 0.2*inch, y, line)
        y -= 0.2 * inch
    
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Primary Outcomes")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    outcomes = [
        "• Mean HbA1c reduction: 1.5% (95% CI: 1.3-1.7%)",
        "• Fasting plasma glucose: reduced by 45 mg/dL",
        "• Time in target range: increased by 25%",
        "• Hypoglycemic events: similar to control (3.2 vs 3.5 events/patient-year)"
    ]
    
    for outcome in outcomes:
        c.drawString(inch + 0.2*inch, y, outcome)
        y -= 0.2 * inch
    
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Dosing Regimen")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    dosing = [
        "• Starting dose: 10 units once daily at bedtime",
        "• Titration: Increase by 2 units every 3 days based on fasting glucose",
        "• Target fasting glucose: 80-130 mg/dL",
        "• Maximum dose: 60 units daily"
    ]
    
    for dose in dosing:
        c.drawString(inch + 0.2*inch, y, dose)
        y -= 0.2 * inch
    
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Common Side Effects")
    y -= 0.25 * inch
    
    c.setFont("Helvetica", 11)
    effects = [
        "• Injection site reactions: 12%",
        "• Mild hypoglycemia: 8%",
        "• Weight gain: average 2.3 kg over 24 weeks",
        "• Nausea: 4%"
    ]
    
    for effect in effects:
        c.drawString(inch + 0.2*inch, y, effect)
        y -= 0.2 * inch
    
    c.save()
    print(f"✅ Created: {filename}")
    return filename


def main():
    print("📝 Creating sample medical PDFs...")
    print()
    
    files = []
    
    try:
        f1 = create_clinical_trial_pdf()
        files.append(f1)
    except Exception as e:
        print(f"❌ Error creating clinical trial PDF: {e}")
    
    try:
        f2 = create_diabetes_study_pdf()
        files.append(f2)
    except Exception as e:
        print(f"❌ Error creating diabetes study PDF: {e}")
    
    print()
    print("=" * 60)
    print("✅ PDF Creation Complete!")
    print("=" * 60)
    print()
    print("📁 Created files:")
    for f in files:
        print(f"   • {f}")
    print()
    print("🚀 These are real PDFs ready to upload!")


if __name__ == "__main__":
    main()
