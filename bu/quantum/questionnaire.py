"""Quantum Questionnaire — PQC readiness, cryptographic landscape, migration planning."""

QUESTIONNAIRE = {
    "bu": "quantum",
    "sections": [
        {
            "id": "S1",
            "title": "Cryptographic Landscape",
            "questions": [
                {"id": "Q1", "text": "What is the primary driver for quantum security assessment?", "type": "choice",
                 "options": ["Regulatory requirement (NIST/NSA CNSA 2.0)", "Board/executive mandate", "Proactive risk management", "Customer/partner requirement"],
                 "branch": {
                     "Regulatory requirement (NIST/NSA CNSA 2.0)": ["Q1a"],
                     "Board/executive mandate": ["Q1b"],
                     "Proactive risk management": [],
                     "Customer/partner requirement": ["Q1c"],
                 }},
                {"id": "Q1a", "text": "Which specific regulation or standard must be complied with? What is the deadline?", "type": "text", "branch_of": "Regulatory requirement (NIST/NSA CNSA 2.0)"},
                {"id": "Q1b", "text": "What is the board's stated timeline for post-quantum migration?", "type": "text", "branch_of": "Board/executive mandate"},
                {"id": "Q1c", "text": "Which customer or partner has issued the quantum security requirement?", "type": "text", "branch_of": "Customer/partner requirement"},
                {"id": "Q2", "text": "What cryptographic algorithms are currently deployed? (RSA, ECC, AES, etc.)", "type": "text"},
                {"id": "Q3", "text": "Do you have a PKI infrastructure? If yes, describe its scale.", "type": "text"},
                {"id": "Q4", "text": "Are TLS certificates and VPN infrastructure included in the assessment scope?", "type": "yesno"},
            ]
        },
        {
            "id": "S2",
            "title": "Migration Readiness",
            "questions": [
                {"id": "Q5", "text": "Has a cryptographic inventory been conducted previously?", "type": "yesno"},
                {"id": "Q6", "text": "Are there legacy systems or applications that cannot easily be updated?", "type": "yesno",
                 "branch": {"Yes": ["Q6a"], "No": []}},
                {"id": "Q6a", "text": "Which legacy systems are likely migration blockers?", "type": "text", "branch_of": "Yes"},
                {"id": "Q7", "text": "What is your preferred NIST PQC algorithm preference: CRYSTALS-Kyber, CRYSTALS-Dilithium, SPHINCS+?", "type": "text"},
                {"id": "Q8", "text": "Is a hybrid classical-quantum transition architecture required?", "type": "yesno"},
            ]
        },
        {
            "id": "S3",
            "title": "Organisational Context",
            "questions": [
                {"id": "Q9", "text": "What industry sector does the organisation operate in?", "type": "text"},
                {"id": "Q10", "text": "What is the organisation's approximate size in terms of employees and IT assets?", "type": "text"},
                {"id": "Q11", "text": "Is a board-level presentation on quantum risk required as a deliverable?", "type": "yesno"},
                {"id": "Q12", "text": "What is the target timeline for completing the PQC migration?", "type": "choice",
                 "options": ["1-2 years", "3-5 years", "5-10 years", "No specific timeline"]},
            ]
        },
    ]
}


def get_questionnaire():
    return QUESTIONNAIRE


def map_to_scope_context(answers: dict) -> str:
    driver = answers.get("Q1", "Not specified")
    algorithms = answers.get("Q2", "Not specified")
    has_pki = answers.get("Q3", "Not specified")
    sector = answers.get("Q9", "Not specified")
    timeline = answers.get("Q12", "Not specified")

    lines = [
        f"**Assessment Driver:** {driver}",
        f"**Current Cryptographic Algorithms:** {algorithms}",
        f"**PKI Infrastructure:** {has_pki}",
        f"**Industry Sector:** {sector}",
        f"**PQC Migration Timeline:** {timeline}",
        f"**Hybrid Architecture Required:** {answers.get('Q8', 'No')}",
    ]
    return "\n".join(lines)
