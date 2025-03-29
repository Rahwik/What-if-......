import google.generativeai as genai
import json
import random
from datetime import datetime

genai.configure(api_key="AIzaSyDRQoxtRJs-GMX3rUQV9nNoOEtJj55_zJc")
model = genai.GenerativeModel('gemini-1.5-flash')

class FairyTaleAgent:
    def __init__(self):
        self.memory_file = 'memory.json'
        self.load_memory()

    def load_memory(self):
        try:
            with open(self.memory_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    self.memory = {"stories": [], "feedback": {}}
                    self.save_memory()
                else:
                    self.memory = json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory = {"stories": [], "feedback": {}}
            self.save_memory()

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def suggest_scenario(self):
        scenarios = [
            "What if dinosaurs could speak?",
            "What if knights had dragons as companions?",
            "What if mermaids were real and lived among us?",
            "What if trees could sing?",
            "What if animals ruled the kingdom?",
            "What if the moon was made of candy?"
        ]
        return random.choice(scenarios)

    def generate_story(self, scenario, iteration=1):
        prompt = (
            f"Write a whimsical fairy tale beginning with 'Once upon a time' based on this scenario: {scenario}. "
            f"Include magical elements, colorful characters (like talking animals, brave knights, or mystical beings), "
            f"a sprinkle of adventure, and a heartwarming resolution. Keep it 500 words, enchanting, and suitable for all ages."
        )
        response = model.generate_content(prompt)
        story = response.text
        story_id = f"{scenario}_{datetime.now().isoformat()}"
        self.memory["stories"].append({"id": story_id, "story": story})
        self.save_memory()
        return story, story_id

    def refine_story(self, story_id, feedback):
        original_story = next(s for s in self.memory["stories"] if s["id"] == story_id)["story"]
        prompt = (
            f"Refine this fairy tale: {original_story}\n"
            f"User feedback: {feedback}\n"
            f"Enhance it with more whimsy and magic, keeping it 500 words and maintaining a fairy tale tone."
        )
        response = model.generate_content(prompt)
        refined_story = response.text
        self.memory["feedback"][story_id] = feedback
        self.memory["stories"] = [s for s in self.memory["stories"] if s["id"] != story_id]
        self.memory["stories"].append({"id": story_id, "story": refined_story})
        self.save_memory()
        return refined_story

    def proactive_story(self):
        scenario = self.suggest_scenario()
        story, _ = self.generate_story(scenario)
        return f"Here’s a magical tale for you: {scenario}\n\n{story}"
