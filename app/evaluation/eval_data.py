"""
Evaluation data for testing insurance chatbot responses.
Contains questions and ground truth answers for various insurance topics.
"""

import pandas as pd

# Comprehensive evaluation dataset for insurance chatbot
eval_data = pd.DataFrame(
    {
        "inputs": [
            # Auto Insurance Questions
            "What does liability insurance cover?",
            "How do I file a car insurance claim?",
            "What is comprehensive coverage?",
            "Do I need uninsured motorist coverage?",
            "What factors affect my auto insurance premium?",
            # Home Insurance Questions
            "Is flood damage covered under homeowners insurance?",
            "What's the difference between replacement cost and actual cash value?",
            "Does homeowners insurance cover personal belongings?",
            "What is a deductible in homeowners insurance?",
            "Are earthquakes covered by standard homeowners insurance?",
            # Life Insurance Questions
            "What's the difference between term and whole life insurance?",
            "How much life insurance do I need?",
            "Can I borrow against my life insurance policy?",
            "What happens if I stop paying life insurance premiums?",
            "Is life insurance taxable to beneficiaries?",
            # Health Insurance Questions
            "What is a health insurance copay?",
            "What's the difference between HMO and PPO?",
            "What does out-of-network mean?",
            "Can I keep my insurance if I lose my job?",
            "What is an HSA?",
            # General Insurance Questions
            "Can I cancel my policy anytime?",
            "What is an insurance premium?",
            "How do insurance companies determine risk?",
            "What should I do after an accident?",
            "Why do I need insurance?",
        ],
        "ground_truth": [
            # Auto Insurance Answers
            "Liability insurance covers costs if you're found legally responsible for someone else's injury or property damage. "
            "It typically includes bodily injury liability and property damage liability, helping pay for medical expenses, "
            "legal fees, and property repairs for the other party.",
            "To file a car insurance claim, contact your insurance provider immediately after an accident. Provide details "
            "including time, location, parties involved, and photos. Get a police report if required. Your insurer will "
            "assign a claims adjuster and guide you through the process.",
            "Comprehensive coverage protects against damage to your vehicle from non-collision events like theft, vandalism, "
            "weather damage, falling objects, or hitting an animal. It's optional unless required by your lender.",
            "Uninsured motorist coverage protects you if you're hit by a driver without insurance or insufficient coverage. "
            "While not required in all states, it's highly recommended as many drivers are underinsured or uninsured.",
            "Auto insurance premiums are affected by factors including your driving record, age, location, vehicle type, "
            "credit score, coverage amounts, deductibles, and annual mileage. Safe drivers with good credit typically pay less.",
            # Home Insurance Answers
            "Standard homeowners insurance policies usually do not cover flood damage. You need a separate flood insurance "
            "policy, often purchased through the National Flood Insurance Program (NFIP) or private insurers.",
            "Replacement cost coverage pays to rebuild or replace your home and belongings at current prices. Actual cash "
            "value coverage pays the depreciated value, accounting for age and wear. Replacement cost typically costs more "
            "but provides better protection.",
            "Yes, homeowners insurance includes personal property coverage for your belongings like furniture, clothing, "
            "and electronics. Coverage is typically 50-70% of your dwelling coverage amount, with limits on high-value items.",
            "A deductible is the amount you pay out-of-pocket before insurance coverage begins. For example, with a $1,000 "
            "deductible and $5,000 in damage, you pay $1,000 and insurance pays $4,000. Higher deductibles mean lower premiums.",
            "Standard homeowners insurance does not cover earthquake damage. You need separate earthquake insurance, "
            "which is especially important in high-risk areas like California. Coverage includes dwelling, personal property, "
            "and additional living expenses.",
            # Life Insurance Answers
            "Term life insurance provides coverage for a specific time period (10-30 years) and pays out only if the insured "
            "dies during that term. Whole life insurance offers lifetime coverage with a cash value component that grows over time "
            "and can be borrowed against.",
            "A common rule is 10-12 times your annual income, but consider your debts, dependents, future expenses like college, "
            "and existing assets. The goal is to ensure your beneficiaries can maintain their lifestyle and meet financial obligations.",
            "Yes, with permanent life insurance policies like whole or universal life, you can borrow against the cash value. "
            "The loan accrues interest, and unpaid loans reduce the death benefit. Term life insurance has no cash value to borrow against.",
            "If you stop paying premiums, term life insurance will lapse and coverage ends. Permanent life insurance may use "
            "cash value to pay premiums temporarily, enter a grace period, or convert to reduced paid-up insurance depending on the policy.",
            "Life insurance death benefits are generally not taxable income to beneficiaries. However, any interest earned on "
            "benefits that are paid in installments may be taxable. Estate taxes may apply for very large policies.",
            # Health Insurance Answers
            "A copay is a fixed amount you pay for covered healthcare services, typically paid at the time of service. "
            "For example, you might pay a $25 copay for a doctor visit or $10 for prescription drugs, with insurance covering the rest.",
            "HMO (Health Maintenance Organization) requires you to choose a primary care physician and get referrals for specialists, "
            "typically with lower costs. PPO (Preferred Provider Organization) offers more flexibility to see any provider without "
            "referrals but usually costs more.",
            "Out-of-network means healthcare providers who don't have contracts with your insurance plan. Using out-of-network "
            "providers typically results in higher costs or no coverage, except in emergencies.",
            "You may be eligible for COBRA continuation coverage, which allows you to keep your employer's plan for up to 18-36 months "
            "by paying the full premium. You can also shop for individual coverage through the Health Insurance Marketplace.",
            "A Health Savings Account (HSA) is a tax-advantaged account for medical expenses, available with high-deductible health plans. "
            "Contributions are tax-deductible, earnings grow tax-free, and withdrawals for qualified medical expenses are tax-free.",
            # General Insurance Answers
            "Most insurance policies allow you to cancel at any time by providing written notice to your insurer. However, "
            "you may face cancellation fees, and some policies require minimum periods. You may receive a prorated refund of unused premiums.",
            "An insurance premium is the amount you pay for your insurance coverage, typically monthly, quarterly, or annually. "
            "Premiums are determined by risk factors, coverage amounts, deductibles, and the insurance company's pricing model.",
            "Insurance companies assess risk using factors like your claims history, demographics, location, credit score, and "
            "specific risks related to what you're insuring. They use statistical models and actuarial data to predict likelihood of claims.",
            "After an accident, ensure everyone's safety and call emergency services if needed. Exchange information with other parties, "
            "take photos, get witness contacts, and file a police report. Contact your insurance company as soon as possible to report the claim.",
            "Insurance protects you financially from unexpected events that could be financially devastating. It provides peace of mind, "
            "helps you comply with legal requirements, protects your assets, and ensures you can recover from covered losses without "
            "depleting your savings.",
        ],
    }
)


def get_eval_dataset():
    """Get the evaluation dataset as a pandas DataFrame."""
    return eval_data.copy()


def get_question_categories():
    """Get questions organized by insurance category."""
    categories = {
        "Auto Insurance": eval_data.iloc[0:5],
        "Home Insurance": eval_data.iloc[5:10],
        "Life Insurance": eval_data.iloc[10:15],
        "Health Insurance": eval_data.iloc[15:20],
        "General Insurance": eval_data.iloc[20:25],
    }
    return categories


def save_eval_data(filename="eval_data.csv"):
    """Save evaluation data to CSV file."""
    eval_data.to_csv(filename, index=False)
    print(f"Evaluation data saved to {filename}")


if __name__ == "__main__":
    print(f"Evaluation dataset contains {len(eval_data)} question-answer pairs")
    print("\nCategories:")
    for category, data in get_question_categories().items():
        print(f"- {category}: {len(data)} questions")

    print(f"\nFirst question: {eval_data.iloc[0]['inputs']}")
    print(f"Ground truth: {eval_data.iloc[0]['ground_truth'][:100]}...")
