"""Questionnaire Agent — runs discovery questionnaire for each BU using AI-simulated Q&A."""
import os
import importlib
from .base_agent import BaseAgent

os.environ.setdefault("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

QUESTIONNAIRE_PROMPT = """You are a Proposal Engine pre-sales specialist running a discovery questionnaire.
Based on the client context provided, simulate realistic answers to the following questionnaire questions.
Generate answers that are consistent with the client's industry, size, region, and likely security posture.

Client: {client_name}
Industry: {industry}
Size: {size}
Region: {region}
Service: {service_name}
BU: {bu}
Exec Summary Context: {exec_summary}

Questions to answer:
{questions_text}

Output a JSON object where each key is the question ID and the value is the simulated answer.
For yes/no questions use "Yes" or "No".
For choice questions use one of the provided options exactly.
For multiselect questions use a list of selected options.
For text questions provide a realistic 1-2 sentence answer.

Output ONLY the JSON object, no other text."""


class QuestionnaireAgent(BaseAgent):
    def run(self, bu: str, sub_bu: str = "", client_info: dict = None, mode: str = "ai") -> dict:
        """Run questionnaire for the given BU.

        Args:
            bu: Business unit code (dfir, mxdr, dpg, cts, institute, quantum)
            sub_bu: Sub-business unit (optional)
            client_info: Client context dict
            mode: 'ai' (default) uses Groq to simulate answers

        Returns:
            dict with 'answers', 'scope_context', 'questionnaire_data'
        """
        if client_info is None:
            client_info = {}

        questionnaire_data = self._load_questionnaire(bu)
        if not questionnaire_data:
            return {
                "answers": {},
                "scope_context": "",
                "questionnaire_data": {},
            }

        # Determine which questions to ask based on sub_bu / service context
        flat_questions = self._flatten_questions(questionnaire_data, sub_bu)

        if mode == "ai":
            answers = self._ai_simulate_answers(flat_questions, questionnaire_data, client_info, bu)
        else:
            answers = self._mock_answers(flat_questions)

        # Map answers to scope context
        scope_context = self._map_to_scope_context(bu, answers)

        return {
            "answers": answers,
            "scope_context": scope_context,
            "questionnaire_data": questionnaire_data,
            "bu": bu,
            "sub_bu": sub_bu,
        }

    def _load_questionnaire(self, bu: str) -> dict:
        """Dynamically load questionnaire from BU module."""
        try:
            module = importlib.import_module(f"bu.{bu}.questionnaire")
            return module.get_questionnaire()
        except (ImportError, AttributeError) as e:
            # Return minimal fallback
            return {
                "bu": bu,
                "sections": [
                    {
                        "id": "S1",
                        "title": "General Discovery",
                        "questions": [
                            {"id": "Q1", "text": "What is the primary driver for this engagement?", "type": "text"},
                            {"id": "Q2", "text": "What is the scope of systems or processes involved?", "type": "text"},
                            {"id": "Q3", "text": "Are there regulatory compliance deadlines?", "type": "text"},
                            {"id": "Q4", "text": "What is the organisation's approximate size?", "type": "text"},
                            {"id": "Q5", "text": "Has a similar assessment been conducted previously?", "type": "yesno"},
                        ]
                    }
                ]
            }

    def _flatten_questions(self, questionnaire_data: dict, sub_bu: str = "") -> list:
        """Flatten all questions from all sections into a single list.
        For sub_bu-specific questionnaires, include relevant branch questions."""
        all_questions = []
        for section in questionnaire_data.get("sections", []):
            for q in section.get("questions", []):
                all_questions.append(q)
        return all_questions

    def _ai_simulate_answers(self, questions: list, questionnaire_data: dict,
                              client_info: dict, bu: str) -> dict:
        """Use Groq to simulate realistic questionnaire answers based on client context."""
        # Build questions text for prompt
        question_lines = []
        # Only include top-level questions (not branch sub-questions) to keep prompt focused
        for q in questions:
            if "branch_of" not in q:
                qtype = q.get("type", "text")
                opts = q.get("options", [])
                line = f'[{q["id"]}] ({qtype}) {q["text"]}'
                if opts:
                    line += f" Options: {opts}"
                question_lines.append(line)

        questions_text = "\n".join(question_lines[:20])  # Limit to avoid token overflow

        prompt = QUESTIONNAIRE_PROMPT.format(
            client_name=client_info.get("name") or "Unknown Client",
            industry=client_info.get("industry") or "Financial Services",
            size=client_info.get("size") or "Mid-market",
            region=client_info.get("region") or "India",
            service_name=self.config.get("name") or bu.upper(),
            bu=bu.upper(),
            exec_summary=client_info.get("exec_summary") or "Not provided",
            questions_text=questions_text,
        )

        try:
            answers = self.call_llm_json(prompt, max_tokens=1024)
        except Exception:
            # Fallback to mock answers
            answers = self._mock_answers(questions)

        return answers

    def _mock_answers(self, questions: list) -> dict:
        """Generate simple mock answers for testing."""
        answers = {}
        for q in questions:
            qtype = q.get("type", "text")
            opts = q.get("options", [])
            if qtype == "yesno":
                answers[q["id"]] = "Yes"
            elif qtype == "choice" and opts:
                answers[q["id"]] = opts[0]
            elif qtype == "multiselect" and opts:
                answers[q["id"]] = [opts[0], opts[1]] if len(opts) > 1 else [opts[0]]
            else:
                answers[q["id"]] = "Standard enterprise environment"
        return answers

    def _map_to_scope_context(self, bu: str, answers: dict) -> str:
        """Map questionnaire answers to scope context string via BU-specific mapper."""
        try:
            module = importlib.import_module(f"bu.{bu}.questionnaire")
            return module.map_to_scope_context(answers)
        except (ImportError, AttributeError):
            # Generic fallback
            lines = []
            for k, v in list(answers.items())[:6]:
                if v and str(v) not in ("", "[]"):
                    lines.append(f"**{k}:** {v}")
            return "\n".join(lines)
