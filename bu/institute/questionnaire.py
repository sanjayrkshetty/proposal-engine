"""Institute Questionnaire — training needs, audience, certification goals."""

QUESTIONNAIRE = {
    "bu": "institute",
    "sections": [
        {
            "id": "S1",
            "title": "Training Needs Assessment",
            "questions": [
                {"id": "Q1", "text": "What type of training programme is required?", "type": "choice",
                 "options": ["Security Awareness (all staff)", "DFIR Certification (analysts)", "SOC Analyst Development", "Executive Cyber Briefing"],
                 "branch": {
                     "Security Awareness (all staff)": ["Q1a", "Q1b"],
                     "DFIR Certification (analysts)": ["Q1c", "Q1d"],
                     "SOC Analyst Development": ["Q1e", "Q1f"],
                     "Executive Cyber Briefing": ["Q1g", "Q1h"],
                 }},
                {"id": "Q1a", "text": "Has a phishing simulation been conducted previously?", "type": "yesno", "branch_of": "Security Awareness (all staff)"},
                {"id": "Q1b", "text": "What awareness topics are highest priority? (e.g., phishing, social engineering, data handling)", "type": "text", "branch_of": "Security Awareness (all staff)"},
                {"id": "Q1c", "text": "What is the current experience level of analysts?", "type": "choice", "options": ["Junior (0-2 years)", "Mid-level (2-5 years)", "Senior (5+ years)"], "branch_of": "DFIR Certification (analysts)"},
                {"id": "Q1d", "text": "Are participants targeting GCFA, GCIH, or a vendor DFIR certification?", "type": "text", "branch_of": "DFIR Certification (analysts)"},
                {"id": "Q1e", "text": "Are you building a new SOC or upskilling an existing team?", "type": "choice", "options": ["New SOC build", "Upskilling existing team"], "branch_of": "SOC Analyst Development"},
                {"id": "Q1f", "text": "Which L1/L2/L3 analyst tracks are required?", "type": "multiselect", "options": ["L1 Alert Triage", "L2 Investigation", "L3 Threat Hunting"], "branch_of": "SOC Analyst Development"},
                {"id": "Q1g", "text": "What is the executive audience's technical background?", "type": "choice", "options": ["Non-technical", "Semi-technical", "Technical"], "branch_of": "Executive Cyber Briefing"},
                {"id": "Q1h", "text": "What key cyber topics should be covered for executives?", "type": "text", "branch_of": "Executive Cyber Briefing"},
            ]
        },
        {
            "id": "S2",
            "title": "Audience & Logistics",
            "questions": [
                {"id": "Q2", "text": "How many participants will attend the training programme?", "type": "text"},
                {"id": "Q3", "text": "Is delivery required on-site, virtual, or blended?", "type": "choice", "options": ["On-site", "Virtual", "Blended"]},
                {"id": "Q4", "text": "Is there a specific deadline or regulatory requirement driving the training timeline?", "type": "text"},
                {"id": "Q5", "text": "Is a formal completion certificate required for compliance evidence?", "type": "yesno"},
            ]
        },
        {
            "id": "S3",
            "title": "Compliance & Outcomes",
            "questions": [
                {"id": "Q6", "text": "Which regulations require security training for your organisation?", "type": "multiselect",
                 "options": ["PCI DSS v4.0 (Req 12.6)", "ISO 27001", "RBI CSF", "DPDP Act 2023", "MAS TRM", "None"]},
                {"id": "Q7", "text": "What is the primary success metric for this programme?", "type": "choice",
                 "options": ["Compliance evidence", "Measurable phishing click-rate reduction", "Staff certification", "SOC capability uplift"]},
                {"id": "Q8", "text": "Do you require post-training assessment and reporting?", "type": "yesno"},
            ]
        },
    ]
}


def get_questionnaire():
    return QUESTIONNAIRE


def map_to_scope_context(answers: dict) -> str:
    programme = answers.get("Q1", "Not specified")
    participants = answers.get("Q2", "Not specified")
    delivery = answers.get("Q3", "Not specified")
    regulations = answers.get("Q6", [])
    if isinstance(regulations, list):
        reg_str = ", ".join(regulations)
    else:
        reg_str = str(regulations)

    lines = [
        f"**Programme Type:** {programme}",
        f"**Participants:** {participants}",
        f"**Delivery Mode:** {delivery}",
        f"**Compliance Drivers:** {reg_str}",
        f"**Success Metric:** {answers.get('Q7', 'Not specified')}",
    ]
    return "\n".join(lines)
