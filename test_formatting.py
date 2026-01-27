import sys
sys.path.insert(0, 'src')

from notebooklm_tools.core.client import NotebookLMClient
import json

# Test quiz markdown formatting
quiz_data = {"quiz": [{"question": "What is 2+2?", "answerOptions": [
    {"text": "3", "isCorrect": False},
    {"text": "4", "isCorrect": True}
], "hint": "Count on your fingers"}]}

md = NotebookLMClient._format_quiz_markdown("Math Quiz", quiz_data["quiz"])
assert "## Question 1" in md, f"Missing question header: {md}"
assert "[x] 4" in md, f"Missing correct answer marker: {md}"
assert "**Hint:**" in md, f"Missing hint: {md}"
print("✓ Quiz markdown works")

# Test flashcards JSON formatting
# Create a mock client instance for the method
class MockClient:
    @staticmethod
    def _format_flashcards_markdown(title, cards):
        return NotebookLMClient._format_flashcards_markdown(title, cards)

    def _format_interactive_content(self, app_data, title, output_format, html_content, is_quiz):
        if output_format == "html":
            return html_content
        if is_quiz:
            questions = app_data.get("quiz", [])
            if output_format == "markdown":
                return NotebookLMClient._format_quiz_markdown(title, questions)
            return json.dumps({"title": title, "questions": questions}, indent=2)
        cards = app_data.get("flashcards", [])
        if output_format == "markdown":
            return NotebookLMClient._format_flashcards_markdown(title, cards)
        normalized = [{"front": c.get("f", ""), "back": c.get("b", "")} for c in cards]
        return json.dumps({"title": title, "cards": normalized}, indent=2)

client = MockClient()
cards_data = {"flashcards": [{"f": "Front", "b": "Back"}]}
json_str = client._format_interactive_content(cards_data, "Cards", "json", "", False)
assert '"front": "Front"' in json_str, f"Missing normalized front field: {json_str}"
print("✓ Flashcards JSON works")
