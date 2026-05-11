"""CTS Questionnaire — cyber testing services with sub-BU branching (PaySec, Warlabs, NetSec, AppSec)."""

QUESTIONNAIRE = {
    "bu": "cts",
    "sections": [
        {
            "id": "S1",
            "title": "Testing Service Type",
            "questions": [
                {
                    "id": "Q1",
                    "text": "What type of security testing is required?",
                    "type": "choice",
                    "options": ["Payment Security (PCI DSS/SSF)", "Red Team / Adversarial Simulation", "Network Penetration Test", "Web Application / API Security", "Static Code Review (SAST)"],
                    "branch": {
                        "Payment Security (PCI DSS/SSF)": ["Q_PAY1", "Q_PAY2", "Q_PAY3", "Q_PAY4"],
                        "Red Team / Adversarial Simulation": ["Q_RT1", "Q_RT2", "Q_RT3", "Q_RT4"],
                        "Network Penetration Test": ["Q_NET1", "Q_NET2", "Q_NET3", "Q_NET4"],
                        "Web Application / API Security": ["Q_APP1", "Q_APP2", "Q_APP3", "Q_APP4"],
                        "Static Code Review (SAST)": ["Q_SAST1", "Q_SAST2", "Q_SAST3", "Q_SAST4"],
                    }
                },
                # Payment Security branch
                {"id": "Q_PAY1", "text": "Are you pursuing PCI DSS v4.0 certification or SSF certification?", "type": "choice", "options": ["PCI DSS v4.0", "PCI SSF", "Both"], "branch_of": "Payment Security (PCI DSS/SSF)"},
                {"id": "Q_PAY2", "text": "Describe your cardholder data environment (CDE) — number of payment channels, systems?", "type": "text", "branch_of": "Payment Security (PCI DSS/SSF)"},
                {"id": "Q_PAY3", "text": "Have you previously completed a PCI assessment? What was your last compliance status?", "type": "text", "branch_of": "Payment Security (PCI DSS/SSF)"},
                {"id": "Q_PAY4", "text": "Is a QSA-issued RoC required, or will an SAQ suffice?", "type": "choice", "options": ["RoC (QSA required)", "SAQ", "Unsure"], "branch_of": "Payment Security (PCI DSS/SSF)"},
                # Red Team branch
                {"id": "Q_RT1", "text": "What is the primary objective of the red team exercise?", "type": "choice", "options": ["Test detection & response capability", "DORA TLPT compliance", "Executive/board assurance", "Post-incident validation"], "branch_of": "Red Team / Adversarial Simulation"},
                {"id": "Q_RT2", "text": "What are the crown jewels — critical systems/data the red team should attempt to reach?", "type": "text", "branch_of": "Red Team / Adversarial Simulation"},
                {"id": "Q_RT3", "text": "Is physical security testing (tailgating, badge cloning) in scope?", "type": "yesno", "branch_of": "Red Team / Adversarial Simulation"},
                {"id": "Q_RT4", "text": "Should a purple team debrief be included (joint attacker/defender exercise)?", "type": "yesno", "branch_of": "Red Team / Adversarial Simulation"},
                # Network Pentest branch
                {"id": "Q_NET1", "text": "Is this an external, internal, or combined network penetration test?", "type": "choice", "options": ["External only", "Internal only", "External + Internal"], "branch_of": "Network Penetration Test"},
                {"id": "Q_NET2", "text": "Approximately how many subnets or IP ranges are in scope?", "type": "text", "branch_of": "Network Penetration Test"},
                {"id": "Q_NET3", "text": "Are Active Directory or domain environments in scope?", "type": "yesno", "branch_of": "Network Penetration Test"},
                {"id": "Q_NET4", "text": "What is the primary driver — compliance (PCI/RBI), cyber insurance, or security improvement?", "type": "text", "branch_of": "Network Penetration Test"},
                # Web App branch
                {"id": "Q_APP1", "text": "How many web applications are in scope?", "type": "text", "branch_of": "Web Application / API Security"},
                {"id": "Q_APP2", "text": "Are APIs (REST/SOAP/GraphQL) to be included in the assessment?", "type": "yesno", "branch_of": "Web Application / API Security"},
                {"id": "Q_APP3", "text": "Is authentication testing (SSO, OAuth, MFA bypass) in scope?", "type": "yesno", "branch_of": "Web Application / API Security"},
                {"id": "Q_APP4", "text": "Is this for PCI DSS compliance (Requirement 6/11), DPDP Act, or general security assurance?", "type": "text", "branch_of": "Web Application / API Security"},
                # SAST branch
                {"id": "Q_SAST1", "text": "What programming languages are in use?", "type": "text", "branch_of": "Static Code Review (SAST)"},
                {"id": "Q_SAST2", "text": "Approximately how many lines of code or repositories are in scope?", "type": "text", "branch_of": "Static Code Review (SAST)"},
                {"id": "Q_SAST3", "text": "Is CI/CD pipeline integration advisory included in scope?", "type": "yesno", "branch_of": "Static Code Review (SAST)"},
                {"id": "Q_SAST4", "text": "Is dependency/SCA scanning (third-party library vulnerabilities) required?", "type": "yesno", "branch_of": "Static Code Review (SAST)"},
            ]
        },
        {
            "id": "S2",
            "title": "Common — Scope & Compliance",
            "questions": [
                {"id": "Q2", "text": "What is the primary compliance or business driver for this engagement?", "type": "text"},
                {"id": "Q3", "text": "Is there a regulatory deadline or audit date driving this timeline?", "type": "text"},
                {"id": "Q4", "text": "Has a similar test been conducted before? What were the key findings?", "type": "text"},
                {"id": "Q5", "text": "Are there any restricted testing windows or blackout periods?", "type": "text"},
            ]
        },
    ]
}


def get_questionnaire():
    return QUESTIONNAIRE


def map_to_scope_context(answers: dict) -> str:
    test_type = answers.get("Q1", "Not specified")
    driver = answers.get("Q2", "Not specified")
    deadline = answers.get("Q3", "None")

    lines = [
        f"**Testing Type:** {test_type}",
        f"**Compliance/Business Driver:** {driver}",
        f"**Regulatory Deadline:** {deadline}",
    ]

    # Sub-BU specific context
    if "Payment" in str(test_type):
        lines.append(f"**Certification Target:** {answers.get('Q_PAY1', 'Not specified')}")
        lines.append(f"**CDE Description:** {answers.get('Q_PAY2', 'Not specified')}")
    elif "Red Team" in str(test_type):
        lines.append(f"**Objective:** {answers.get('Q_RT1', 'Not specified')}")
        lines.append(f"**Crown Jewels:** {answers.get('Q_RT2', 'Not specified')}")
    elif "Network" in str(test_type):
        lines.append(f"**Test Scope:** {answers.get('Q_NET1', 'Not specified')}")
        lines.append(f"**Subnets in Scope:** {answers.get('Q_NET2', 'Not specified')}")
    elif "Web Application" in str(test_type):
        lines.append(f"**Applications in Scope:** {answers.get('Q_APP1', 'Not specified')}")
        lines.append(f"**APIs in Scope:** {answers.get('Q_APP2', 'No')}")
    elif "SAST" in str(test_type):
        lines.append(f"**Languages:** {answers.get('Q_SAST1', 'Not specified')}")
        lines.append(f"**Codebase Size:** {answers.get('Q_SAST2', 'Not specified')}")

    return "\n".join(lines)
