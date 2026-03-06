#!/usr/bin/env python3
"""
Download test medical documents from HuggingFace datasets
"""

import os
from pathlib import Path

def download_from_pubmed():
    """Download sample medical PDFs from PubMed Central"""
    import urllib.request
    
    # Create test_documents directory
    docs_dir = Path("test_documents")
    docs_dir.mkdir(exist_ok=True)
    
    print("📥 Downloading test medical documents from PubMed Central...")
    print()
    
    # Sample medical research papers (open access)
    # Using direct arxiv/biorxiv links that work reliably
    papers = [
        {
            "url": "https://www.medrxiv.org/content/10.1101/2020.04.17.20069773v2.full.pdf",
            "filename": "covid19_clinical_trial.pdf",
            "title": "COVID-19 Clinical Trial"
        },
        {
            "url": "https://www.biorxiv.org/content/10.1101/2021.06.15.448494v1.full.pdf",
            "filename": "diabetes_treatment.pdf",
            "title": "Diabetes Treatment Study"
        },
        {
            "url": "https://arxiv.org/pdf/2103.14030.pdf",
            "filename": "ml_healthcare.pdf",
            "title": "ML in Healthcare Research"
        }
    ]
    
    downloaded = []
    
    for paper in papers:
        filepath = docs_dir / paper["filename"]
        
        if filepath.exists():
            print(f"✅ {paper['title']} - Already exists")
            downloaded.append(str(filepath))
            continue
        
        try:
            print(f"⏳ Downloading {paper['title']}...")
            urllib.request.urlretrieve(paper["url"], filepath)
            print(f"✅ {paper['title']} - Downloaded")
            downloaded.append(str(filepath))
        except Exception as e:
            print(f"❌ {paper['title']} - Failed: {e}")
    
    print()
    print(f"📊 Downloaded {len(downloaded)} documents")
    print()
    
    if downloaded:
        print("📁 Files saved in:")
        for doc in downloaded:
            print(f"   {doc}")
    
    return downloaded


def download_from_huggingface():
    """Download medical documents from HuggingFace datasets"""
    try:
        from datasets import load_dataset
        import json
        
        print("📥 Loading medical QA dataset from HuggingFace...")
        print()
        
        # Create test_documents directory
        docs_dir = Path("test_documents")
        docs_dir.mkdir(exist_ok=True)
        
        # Load PubMedQA dataset
        print("⏳ Loading PubMedQA dataset...")
        dataset = load_dataset("pubmed_qa", "pqa_labeled", split="train[:10]")
        
        # Save as JSON for now (these are text-based, not PDFs)
        output_file = docs_dir / "pubmedqa_samples.json"
        
        samples = []
        for item in dataset:
            samples.append({
                "question": item.get("question", ""),
                "context": item.get("context", {}).get("contexts", []),
                "answer": item.get("final_decision", "")
            })
        
        with open(output_file, "w") as f:
            json.dump(samples, f, indent=2)
        
        print(f"✅ Saved {len(samples)} medical Q&A samples to {output_file}")
        print()
        print("Note: These are text samples, not PDFs.")
        print("For PDF testing, use the PubMed download option.")
        
        return [str(output_file)]
        
    except ImportError:
        print("⚠️  HuggingFace datasets library not installed")
        print("Install with: pip install datasets")
        return []
    except Exception as e:
        print(f"❌ Error loading from HuggingFace: {e}")
        return []


def create_sample_pdf():
    """Create a simple sample medical PDF"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        
        docs_dir = Path("test_documents")
        docs_dir.mkdir(exist_ok=True)
        
        filename = docs_dir / "sample_clinical_trial.pdf"
        
        if filename.exists():
            print(f"✅ Sample PDF already exists: {filename}")
            return [str(filename)]
        
        print("📝 Creating sample clinical trial PDF...")
        
        c = canvas.Canvas(str(filename), pagesize=letter)
        width, height = letter
        y = height - inch
        
        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawString(inch, y, "Phase III Clinical Trial Protocol")
        y -= 0.3 * inch
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y, "Drug X for Treatment of Hypertension")
        y -= 0.5 * inch
        
        # Content
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, "Primary Endpoint")
        y -= 0.25 * inch
        
        c.setFont("Helvetica", 11)
        text = [
            "• Reduction in systolic blood pressure by ≥10 mmHg from baseline at Week 12",
            "",
            "Secondary Endpoints:",
            "• Reduction in diastolic blood pressure",
            "• Proportion of patients achieving blood pressure control (<140/90 mmHg)",
            "• Safety and tolerability assessment",
            "",
            "Dosing Schedule:",
            "• Drug X: 10mg once daily, taken in the morning",
            "• Administration: Oral tablet with or without food",
            "• Duration: 12 weeks of treatment",
            "",
            "Common Side Effects:",
            "• Headache: 15% of patients",
            "• Dizziness: 8% of patients",
            "• Fatigue: 5% of patients",
            "• Nausea: 3% of patients",
        ]
        
        for line in text:
            c.drawString(inch + 0.2*inch, y, line)
            y -= 0.2 * inch
        
        c.save()
        print(f"✅ Created sample PDF: {filename}")
        return [str(filename)]
        
    except ImportError:
        print("⚠️  reportlab not installed")
        print("Install with: pip install reportlab")
        return []
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        return []


def main():
    print("=" * 60)
    print("📚 Medical Document Downloader")
    print("=" * 60)
    print()
    
    print("Choose an option:")
    print("1. Download from PubMed Central (Recommended - Real PDFs)")
    print("2. Download from HuggingFace (Text samples)")
    print("3. Create sample PDF")
    print("4. All of the above")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    print()
    
    all_files = []
    
    if choice in ["1", "4"]:
        files = download_from_pubmed()
        all_files.extend(files)
        print()
    
    if choice in ["2", "4"]:
        files = download_from_huggingface()
        all_files.extend(files)
        print()
    
    if choice in ["3", "4"]:
        files = create_sample_pdf()
        all_files.extend(files)
        print()
    
    if all_files:
        print("=" * 60)
        print("✅ Download Complete!")
        print("=" * 60)
        print()
        print("📁 Files available for testing:")
        for f in all_files:
            print(f"   • {f}")
        print()
        print("🚀 Next steps:")
        print("   1. Start your application (backend + frontend)")
        print("   2. Upload one of these PDFs")
        print("   3. Ask questions about the document")
    else:
        print("❌ No files downloaded")


if __name__ == "__main__":
    main()
