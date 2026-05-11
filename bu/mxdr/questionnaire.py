"""MXDR Questionnaire — detection maturity, endpoint coverage, compliance requirements."""

QUESTIONNAIRE = {
    "bu": "mxdr",
    "sections": [
        {
            "id": "S1",
            "title": "Current Security Monitoring",
            "questions": [
                {"id": "Q1", "text": "Do you currently have a SIEM deployed?", "type": "yesno",
                 "branch": {"Yes": ["Q1a", "Q1b"], "No": ["Q1c"]}},
                {"id": "Q1a", "text": "Which SIEM platform? (e.g., Splunk, Microsoft Sentinel, IBM QRadar)", "type": "text", "branch_of": "Yes"},
                {"id": "Q1b", "text": "Are you satisfied with the detection coverage? What gaps exist?", "type": "text", "branch_of": "Yes"},
                {"id": "Q1c", "text": "What is driving the decision to implement SIEM/MXDR now?", "type": "text", "branch_of": "No"},
                {"id": "Q2", "text": "Do you have an EDR solution? If yes, which product?", "type": "text"},
                {"id": "Q3", "text": "How many endpoints require monitoring coverage?", "type": "text"},
                {"id": "Q4", "text": "Do you have an internal SOC team? If yes, what are their current responsibilities?", "type": "text"},
            ]
        },
        {
            "id": "S2",
            "title": "Environment & Data Sources",
            "questions": [
                {"id": "Q5", "text": "What cloud platforms are in use? (AWS, Azure, GCP, SaaS apps)", "type": "text"},
                {"id": "Q6", "text": "Are identity platforms (Azure AD, Okta) to be included in monitoring scope?", "type": "yesno"},
                {"id": "Q7", "text": "Are OT/ICS environments to be included? If yes, which protocols?", "type": "yesno",
                 "branch": {"Yes": ["Q7a"], "No": []}},
                {"id": "Q7a", "text": "What OT/ICS protocols are in use? (Modbus, DNP3, OPC-UA, etc.)", "type": "text", "branch_of": "Yes"},
                {"id": "Q8", "text": "Approximate daily log volume (GB/day)?", "type": "text"},
            ]
        },
        {
            "id": "S3",
            "title": "Compliance & Business Requirements",
            "questions": [
                {"id": "Q9", "text": "Which frameworks mandate continuous monitoring for your organisation?", "type": "multiselect",
                 "options": ["MAS TRM", "RBI CSF", "PCI DSS", "ISO 27001", "SEBI", "DORA", "NIS2", "None"]},
                {"id": "Q10", "text": "Is there a board or regulator deadline driving this engagement?", "type": "text"},
                {"id": "Q11", "text": "What is the primary business driver: compliance, security maturity, or cost reduction?", "type": "choice",
                 "options": ["Regulatory compliance", "Security maturity improvement", "Cost reduction vs. in-house SOC", "Post-incident hardening"]},
            ]
        },
    ]
}


def get_questionnaire():
    return QUESTIONNAIRE


def map_to_scope_context(answers: dict) -> str:
    has_siem = answers.get("Q1", "No")
    endpoints = answers.get("Q3", "Not specified")
    cloud = answers.get("Q5", "Not specified")
    frameworks = answers.get("Q9", [])
    if isinstance(frameworks, list):
        frameworks_str = ", ".join(frameworks)
    else:
        frameworks_str = str(frameworks)
    driver = answers.get("Q11", "Not specified")

    lines = [
        f"**SIEM Status:** {'Existing ({})'.format(answers.get('Q1a', '')) if str(has_siem).lower() in ('yes', 'true') else 'Not deployed'}",
        f"**Endpoints in Scope:** {endpoints}",
        f"**Cloud Platforms:** {cloud}",
        f"**Compliance Drivers:** {frameworks_str}",
        f"**Business Driver:** {driver}",
    ]
    return "\n".join(lines)
