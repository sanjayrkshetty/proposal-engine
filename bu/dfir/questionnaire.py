"""DFIR Questionnaire — branching logic for incident type, environment, regulatory, urgency."""

QUESTIONNAIRE = {
    "bu": "dfir",
    "sections": [
        {
            "id": "S1",
            "title": "Incident Type",
            "questions": [
                {
                    "id": "Q1",
                    "text": "What is the nature of the incident or security concern?",
                    "type": "choice",
                    "options": ["Ransomware", "Data Breach", "Insider Threat", "Business Email Compromise (BEC)", "Unknown / Suspicious Activity"],
                    "branch": {
                        "Ransomware": ["Q1a", "Q1b", "Q1c", "Q1d"],
                        "Data Breach": ["Q1e", "Q1f", "Q1g", "Q1h"],
                        "Insider Threat": ["Q1i", "Q1j", "Q1k", "Q1l"],
                        "Business Email Compromise (BEC)": ["Q1m", "Q1n", "Q1o", "Q1p"],
                        "Unknown / Suspicious Activity": ["Q1q", "Q1r", "Q1s", "Q1t"],
                    }
                },
                # Ransomware branch
                {"id": "Q1a", "text": "Has ransomware been deployed and are files encrypted?", "type": "yesno", "branch_of": "Ransomware"},
                {"id": "Q1b", "text": "Have attackers made contact with a ransom demand?", "type": "yesno", "branch_of": "Ransomware"},
                {"id": "Q1c", "text": "Which systems/business units have been impacted?", "type": "text", "branch_of": "Ransomware"},
                {"id": "Q1d", "text": "Are backups intact and tested?", "type": "yesno", "branch_of": "Ransomware"},
                # Data Breach branch
                {"id": "Q1e", "text": "What categories of data may have been exfiltrated?", "type": "text", "branch_of": "Data Breach"},
                {"id": "Q1f", "text": "Approximately how many records are potentially affected?", "type": "text", "branch_of": "Data Breach"},
                {"id": "Q1g", "text": "Was the breach through an external attacker or internal actor?", "type": "choice", "options": ["External", "Internal", "Unknown"], "branch_of": "Data Breach"},
                {"id": "Q1h", "text": "Have you notified any authorities or regulators?", "type": "yesno", "branch_of": "Data Breach"},
                # Insider Threat branch
                {"id": "Q1i", "text": "Is this a current or former employee?", "type": "choice", "options": ["Current", "Former", "Contractor", "Unknown"], "branch_of": "Insider Threat"},
                {"id": "Q1j", "text": "What data or systems were potentially accessed inappropriately?", "type": "text", "branch_of": "Insider Threat"},
                {"id": "Q1k", "text": "Is HR or legal counsel currently involved?", "type": "yesno", "branch_of": "Insider Threat"},
                {"id": "Q1l", "text": "Is the individual still employed/has access?", "type": "yesno", "branch_of": "Insider Threat"},
                # BEC branch
                {"id": "Q1m", "text": "Was a fraudulent payment made? If yes, approximate amount?", "type": "text", "branch_of": "BEC"},
                {"id": "Q1n", "text": "Which email accounts were compromised?", "type": "text", "branch_of": "BEC"},
                {"id": "Q1o", "text": "Has the compromised account been quarantined?", "type": "yesno", "branch_of": "BEC"},
                {"id": "Q1p", "text": "Have you notified your bank or financial institution?", "type": "yesno", "branch_of": "BEC"},
                # Unknown branch
                {"id": "Q1q", "text": "What anomalous activity was first observed?", "type": "text", "branch_of": "Unknown"},
                {"id": "Q1r", "text": "When was the anomaly first noticed?", "type": "text", "branch_of": "Unknown"},
                {"id": "Q1s", "text": "Which systems or users are affected?", "type": "text", "branch_of": "Unknown"},
                {"id": "Q1t", "text": "Have you already engaged any security vendor or tool?", "type": "yesno", "branch_of": "Unknown"},
            ]
        },
        {
            "id": "S2",
            "title": "Environment",
            "questions": [
                {"id": "Q2", "text": "Approximately how many endpoints and servers are in scope?", "type": "text"},
                {"id": "Q3", "text": "Do you have EDR/SIEM tooling currently deployed? If yes, which products?", "type": "text"},
                {"id": "Q4", "text": "Is your environment on-premises, cloud (AWS/Azure/GCP), or hybrid?", "type": "choice", "options": ["On-premises", "Cloud", "Hybrid"]},
                {"id": "Q5", "text": "Is Active Directory or Azure AD in use? Is it potentially compromised?", "type": "text"},
                {"id": "Q5a", "text": "Are there OT/ICS systems in scope?", "type": "yesno"},
            ]
        },
        {
            "id": "S3",
            "title": "Regulatory & Legal",
            "questions": [
                {"id": "Q6", "text": "What industry/sector does your organisation operate in?", "type": "text"},
                {"id": "Q7", "text": "Which regulatory frameworks apply to your organisation?", "type": "multiselect",
                 "options": ["PCI DSS", "RBI Cyber Security Framework", "SEBI CSF", "ISO/IEC 27001", "CERT-In", "DPDP Act 2023", "HIPAA", "GDPR", "MAS TRM", "None"]},
                {"id": "Q8", "text": "Do you have external legal counsel engaged for this incident?", "type": "yesno"},
                {"id": "Q9", "text": "Has law enforcement been notified or is notification expected?", "type": "yesno"},
            ]
        },
        {
            "id": "S4",
            "title": "Urgency & Timeline",
            "questions": [
                {"id": "Q10", "text": "Is the threat active and ongoing right now?", "type": "yesno"},
                {"id": "Q11", "text": "What is the current business impact? (e.g., systems down, operations halted, revenue loss)", "type": "text"},
                {"id": "Q12", "text": "What is your desired engagement start timeline?", "type": "choice",
                 "options": ["Immediate (today/tomorrow)", "Within 48 hours", "Within 1 week", "Planned (no active threat)"]},
                {"id": "Q13", "text": "Do you have a current IR retainer with any vendor? If yes, why are you exploring alternatives?", "type": "text"},
            ]
        },
    ]
}


def get_questionnaire():
    return QUESTIONNAIRE


def map_to_scope_context(answers: dict) -> str:
    """Map questionnaire answers Q1, Q2, Q6, Q7 to a scope context string."""
    lines = []
    incident_type = answers.get("Q1", "Unknown")
    env_size = answers.get("Q2", "Not specified")
    industry = answers.get("Q6", "Not specified")
    frameworks = answers.get("Q7", [])

    if isinstance(frameworks, list):
        frameworks_str = ", ".join(frameworks) if frameworks else "Not specified"
    else:
        frameworks_str = str(frameworks)

    lines.append(f"**Incident Type:** {incident_type}")
    lines.append(f"**Environment Size:** {env_size}")
    lines.append(f"**Industry:** {industry}")
    lines.append(f"**Applicable Frameworks:** {frameworks_str}")

    # Add urgency context
    urgency = answers.get("Q12", "")
    if urgency:
        lines.append(f"**Engagement Timeline:** {urgency}")

    active_threat = answers.get("Q10", "")
    if active_threat:
        lines.append(f"**Active Threat:** {'Yes — immediate response required' if str(active_threat).lower() in ('yes', 'true', '1') else 'No'}")

    return "\n".join(lines)
