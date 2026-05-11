"""DPG Questionnaire — data privacy maturity, processing activities, regulatory exposure."""

QUESTIONNAIRE = {
    "bu": "dpg",
    "sections": [
        {
            "id": "S1",
            "title": "Privacy Programme Maturity",
            "questions": [
                {"id": "Q1", "text": "Do you currently have a designated Data Protection Officer (DPO)?", "type": "yesno",
                 "branch": {"Yes": ["Q1a"], "No": ["Q1b"]}},
                {"id": "Q1a", "text": "Is the DPO internal or outsourced? What are their current responsibilities?", "type": "text", "branch_of": "Yes"},
                {"id": "Q1b", "text": "What is the primary driver for needing a DPO: regulation, board mandate, or customer requirement?", "type": "text", "branch_of": "No"},
                {"id": "Q2", "text": "Do you have a Records of Processing Activities (RoPA) maintained?", "type": "yesno"},
                {"id": "Q3", "text": "Have you conducted a DPIA for any high-risk processing activities previously?", "type": "yesno"},
            ]
        },
        {
            "id": "S2",
            "title": "Processing Activities",
            "questions": [
                {"id": "Q4", "text": "What categories of personal data does your organisation process?", "type": "multiselect",
                 "options": ["Customer PII", "Employee data", "Health/medical data", "Financial data", "Children's data", "Biometric data", "Location data"]},
                {"id": "Q5", "text": "Approximately how many data subjects are affected?", "type": "text"},
                {"id": "Q6", "text": "Do you share personal data with third-party processors or international recipients?", "type": "yesno",
                 "branch": {"Yes": ["Q6a"], "No": []}},
                {"id": "Q6a", "text": "List the key third-party processors and the countries involved in data transfers.", "type": "text", "branch_of": "Yes"},
                {"id": "Q7", "text": "What is the primary purpose of the DPIA or privacy audit?", "type": "choice",
                 "options": ["New product/service launch", "Regulatory requirement", "Post-incident review", "Third-party audit requirement", "Proactive compliance"]},
            ]
        },
        {
            "id": "S3",
            "title": "Regulatory & Legal",
            "questions": [
                {"id": "Q8", "text": "Which privacy regulations apply to your organisation?", "type": "multiselect",
                 "options": ["DPDP Act 2023 (India)", "GDPR (EU)", "PDPA (Singapore)", "POPIA (South Africa)", "HIPAA (US)", "CCPA (US)"]},
                {"id": "Q9", "text": "Have you received any regulatory notices or data subject complaints?", "type": "yesno"},
                {"id": "Q10", "text": "Is there a specific product launch, audit, or regulatory deadline driving this engagement?", "type": "text"},
            ]
        },
    ]
}


def get_questionnaire():
    return QUESTIONNAIRE


def map_to_scope_context(answers: dict) -> str:
    data_categories = answers.get("Q4", [])
    if isinstance(data_categories, list):
        data_str = ", ".join(data_categories)
    else:
        data_str = str(data_categories)
    regulations = answers.get("Q8", [])
    if isinstance(regulations, list):
        reg_str = ", ".join(regulations)
    else:
        reg_str = str(regulations)

    lines = [
        f"**Data Categories Processed:** {data_str}",
        f"**Data Subjects:** {answers.get('Q5', 'Not specified')}",
        f"**Applicable Regulations:** {reg_str}",
        f"**Engagement Driver:** {answers.get('Q7', 'Not specified')}",
        f"**Third-Party Processors:** {'Yes' if str(answers.get('Q6', 'No')).lower() in ('yes', 'true') else 'No'}",
    ]
    return "\n".join(lines)
