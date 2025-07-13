#!/usr/bin/env python3
"""
Seed data script for the LLMOps Insurance Chatbot system.
Populates the raw data directory with sample insurance documents for testing.
"""

import json
import os
from pathlib import Path


def create_sample_documents(data_path: str):
    """Create sample insurance documents for testing the LLMOps system."""
    raw_data_path = Path(data_path) / "raw"
    raw_data_path.mkdir(parents=True, exist_ok=True)

    # Insurance FAQ document
    faq_content = """# SafeGuard Insurance - Frequently Asked Questions

## Claims Processing

### How do I file a claim?
To file a claim with SafeGuard Insurance:
1. Contact our 24/7 claims hotline at 1-800-SAFEGUARD
2. Provide your policy number and basic incident details
3. Submit required documentation within 30 days
4. Schedule an inspection if needed for property claims
5. Receive claim decision within 15 business days

### What documents do I need for a claim?
Required documents vary by claim type:
- **Auto claims**: Police report, photos of damage, other driver's information
- **Home claims**: Photos of damage, repair estimates, receipts for damaged items
- **Health claims**: Medical bills, doctor's notes, prescription receipts
- **Life claims**: Death certificate, policy documents, beneficiary identification

### How long does claim processing take?
Standard processing times:
- Auto claims: 7-10 business days
- Property claims: 10-15 business days
- Health claims: 5-7 business days
- Life insurance claims: 15-30 business days

## Policy Information

### What types of insurance do we offer?
SafeGuard Insurance provides:
- **Auto Insurance**: Liability, collision, comprehensive, uninsured motorist
- **Home Insurance**: Dwelling, personal property, liability, additional living expenses
- **Health Insurance**: Individual, family, and group plans
- **Life Insurance**: Term life, whole life, universal life
- **Business Insurance**: General liability, property, workers' compensation

### How can I update my policy?
Policy updates can be made:
- Online through your customer portal
- By calling customer service at 1-800-CUSTOMER
- Through your local agent
- By mailing completed forms to our processing center

### When are premiums due?
Premium payment schedules:
- Monthly: Due on the same date each month
- Quarterly: Due every 3 months
- Semi-annually: Due every 6 months
- Annually: Due once per year
Grace period: 10 days for monthly, 30 days for other payment schedules

## Coverage Details

### What is a deductible?
A deductible is the amount you pay out-of-pocket before your insurance coverage begins. Higher deductibles typically mean lower premiums. Common deductible amounts:
- Auto: $250, $500, $1,000
- Home: $500, $1,000, $2,500
- Health: Varies by plan

### What factors affect my premium?
Premium factors include:
- **Age and gender**: Younger drivers and males typically pay more for auto
- **Location**: Urban areas often have higher rates
- **Coverage limits**: Higher limits increase premiums
- **Claims history**: Frequent claims may increase rates
- **Credit score**: Better credit often means lower premiums (where allowed by law)
- **Deductible amount**: Higher deductibles lower premiums

## Customer Service

### How can I contact customer service?
Customer service options:
- **Phone**: 1-800-CUSTOMER (24/7)
- **Online**: Customer portal at safeguardinsurance.com
- **Email**: support@safeguardinsurance.com
- **Chat**: Live chat available on website
- **Mobile app**: SafeGuard Mobile App
- **Local agents**: Find an agent at safeguardinsurance.com/agents

### What are your business hours?
- **Claims**: 24/7/365
- **Customer Service**: Monday-Friday 7 AM - 9 PM, Saturday 8 AM - 6 PM
- **Local Agents**: Varies by location
- **Online Services**: Available 24/7
"""

    with open(raw_data_path / "insurance_faq.md", "w") as f:
        f.write(faq_content)

    # Policy information document
    policy_docs = """# SafeGuard Insurance Policy Information

## Auto Insurance Coverage

### Liability Coverage
Protects you when you're at fault in an accident:
- **Bodily Injury Liability**: Covers medical expenses for others
- **Property Damage Liability**: Covers damage to other vehicles/property
- **Minimum required limits vary by state**

### Physical Damage Coverage
Protects your vehicle:
- **Collision**: Covers damage from accidents, regardless of fault
- **Comprehensive**: Covers non-collision damage (theft, vandalism, weather)
- **Required if you have a loan or lease**

### Additional Coverage Options
- **Uninsured/Underinsured Motorist**: Protection when others lack coverage
- **Medical Payments**: Covers medical expenses for you and passengers
- **Rental Reimbursement**: Pays for rental car while yours is being repaired
- **Roadside Assistance**: 24/7 towing and emergency services

## Home Insurance Coverage

### Dwelling Coverage
Protects the structure of your home:
- **Coverage A**: Main dwelling structure
- **Coverage B**: Other structures (garage, shed, fence)
- **Replacement Cost vs. Actual Cash Value options**

### Personal Property Coverage
Protects your belongings:
- **Coverage C**: Personal property (furniture, clothing, electronics)
- **Off-premises coverage**: Items stolen from your car or hotel
- **Special limits apply to jewelry, art, and collectibles**

### Liability and Living Expenses
- **Coverage E**: Personal liability protection
- **Coverage F**: Medical payments to others
- **Coverage G**: Additional living expenses if home is uninhabitable

## Health Insurance Plans

### Plan Types
- **HMO (Health Maintenance Organization)**: Lower costs, referrals required
- **PPO (Preferred Provider Organization)**: More flexibility, higher costs
- **EPO (Exclusive Provider Organization)**: Network restrictions, no referrals
- **HDHP (High Deductible Health Plans)**: Lower premiums, higher deductibles

### Covered Services
- **Preventive care**: Annual check-ups, vaccinations, screenings
- **Emergency services**: Emergency room visits, urgent care
- **Prescription drugs**: Generic and brand-name medications
- **Mental health**: Therapy, counseling, psychiatric services
- **Specialist care**: Cardiologists, dermatologists, etc.

## Life Insurance Options

### Term Life Insurance
- **Level Term**: Premiums stay the same for a specific period
- **Decreasing Term**: Coverage amount decreases over time
- **Convertible Term**: Can be converted to permanent life insurance

### Permanent Life Insurance
- **Whole Life**: Guaranteed death benefit and cash value
- **Universal Life**: Flexible premiums and death benefits
- **Variable Life**: Investment component with market risk

## Claims Process

### Reporting a Claim
1. **Immediate reporting**: Call within 24 hours when possible
2. **Gather information**: Policy number, incident details, photos
3. **Documentation**: Keep all receipts and correspondence
4. **Cooperation**: Work with adjusters and investigators

### Claim Investigation
- **Adjuster assignment**: Within 1 business day
- **Investigation timeline**: Varies by complexity
- **Additional documentation**: May be requested during process
- **Settlement negotiation**: Good faith efforts to reach fair resolution

### Payment Process
- **Settlement agreement**: Review before signing
- **Payment timeline**: Within 5 business days of agreement
- **Payment methods**: Check, direct deposit, or debit card
- **Tax implications**: Consult tax advisor if applicable
"""

    with open(raw_data_path / "policy_information.md", "w") as f:
        f.write(policy_docs)

    # Sample insurance data in JSON format
    insurance_data = [
        {
            "title": "Auto Insurance Discounts",
            "content": "SafeGuard offers various auto insurance discounts: Safe Driver Discount (25% off for 5+ years claim-free), Multi-Policy Discount (15% when bundling auto and home), Good Student Discount (10% for students with B average or better), Defensive Driving Course (5% discount), Anti-theft Device (up to 10% discount), Low Mileage Discount (5-15% for driving less than 7,500 miles annually).",
            "category": "discounts",
            "tags": ["auto", "discounts", "savings"],
        },
        {
            "title": "Filing a Home Insurance Claim",
            "content": "Steps to file a home insurance claim: 1) Ensure safety first, 2) Contact emergency services if needed, 3) Document damage with photos and videos, 4) Call SafeGuard claims hotline at 1-800-SAFEGUARD, 5) Make temporary repairs to prevent further damage, 6) Keep receipts for temporary repairs and living expenses, 7) Meet with the adjuster, 8) Review the settlement offer carefully.",
            "category": "claims",
            "tags": ["home", "claims", "process"],
        },
        {
            "title": "Understanding Health Insurance Networks",
            "content": "Health insurance networks determine your out-of-pocket costs. In-Network providers have contracted rates and lower costs to you. Out-of-Network providers may result in higher costs or no coverage. Always verify provider network status before appointments. Emergency services are typically covered regardless of network status.",
            "category": "health",
            "tags": ["health", "networks", "providers"],
        },
        {
            "title": "Life Insurance Beneficiaries",
            "content": "Beneficiary designation is crucial for life insurance. Primary beneficiaries receive the death benefit first. Contingent beneficiaries receive benefits if primary beneficiaries predecease the insured. You can name multiple beneficiaries and specify percentages. Update beneficiaries after major life events like marriage, divorce, or birth of children.",
            "category": "life insurance",
            "tags": ["life", "beneficiaries", "planning"],
        },
    ]

    with open(raw_data_path / "insurance_articles.json", "w") as f:
        json.dump(insurance_data, f, indent=2)

    # Insurance procedures and guidelines
    procedures_content = """SafeGuard Insurance Procedures and Guidelines

CLAIM HANDLING PROCEDURES

Emergency Claims
- Life-threatening situations: Call 911 first, then SafeGuard
- Property emergencies: Secure the property, then report claim
- Auto accidents: Ensure safety, call police if required, then report

Documentation Requirements
- All claims require policy number and incident date/time
- Photo documentation strongly recommended
- Police reports required for auto accidents and theft
- Medical records required for injury claims
- Repair estimates needed for property damage

CUSTOMER SERVICE STANDARDS

Response Times
- Phone calls answered within 3 rings or 30 seconds
- Emails responded to within 24 hours during business days
- Claims acknowledged within 1 business day
- Claim decisions communicated within policy timeframes

Quality Assurance
- All customer interactions may be recorded for quality
- Customer satisfaction surveys sent after claim resolution
- Regular training for all customer-facing staff
- Complaint escalation process available

UNDERWRITING GUIDELINES

Risk Assessment Factors
- Driving record (auto insurance)
- Credit history (where legally permitted)
- Claims history
- Property location and condition
- Age and experience of insured

Coverage Limitations
- Policy limits clearly defined in declarations page
- Exclusions listed in policy contract
- Deductibles apply per occurrence
- Coverage territory restrictions may apply

PREMIUM BILLING AND PAYMENT

Payment Options
- Automatic bank draft
- Credit/debit card payments
- Online payment portal
- Phone payments
- Mail-in payments

Late Payment Policy
- Grace period varies by payment frequency
- Late fees assessed after grace period
- Policy cancellation for non-payment follows state regulations
- Reinstatement possible within specified timeframes

PRIVACY AND SECURITY

Information Protection
- Customer information protected per privacy policy
- Secure transmission of sensitive data
- Limited access to customer records
- Regular security audits and updates

Fraud Prevention
- Sophisticated fraud detection systems
- Investigation unit for suspicious claims
- Cooperation with law enforcement
- Protection of honest customers through fraud prevention
"""

    with open(raw_data_path / "insurance_procedures.txt", "w") as f:
        f.write(procedures_content)

    print(f"✅ Insurance sample documents created in {raw_data_path}")
    print("Files created:")
    print("- insurance_faq.md")
    print("- policy_information.md")
    print("- insurance_articles.json")
    print("- insurance_procedures.txt")


def main():
    """Main function to seed the data directory."""
    # Get the data path relative to the script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_path = project_root / "data"

    create_sample_documents(str(data_path))


if __name__ == "__main__":
    main()
