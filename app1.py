from flask import Flask, render_template, request
import requests
import os
import json
from agent import FairyTaleAgent

app = Flask(__name__)
agent = FairyTaleAgent()

IMAGE_API_KEY = "YOUR_DEEPAI_API_KEY"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'generate':
            scenario = request.form.get('scenario', '').strip()
            if not scenario:
                scenario = agent.suggest_scenario()
            try:
                story, story_id = agent.generate_story(scenario)
                return render_template('index.html', story=story, story_id=story_id, scenario=scenario)
            except Exception as e:
                return render_template('index.html', error=f"Error: {str(e)}")

        elif action == 'refine':
            story_id = request.form.get('story_id')
            feedback = request.form.get('feedback')
            if story_id and feedback:
                try:
                    refined_story = agent.refine_story(story_id, feedback)
                    scenario = story_id.split('_')[0]
                    return render_template('index.html', story=refined_story, story_id=story_id, scenario=scenario)
                except Exception as e:
                    return render_template('index.html', error=f"Error refining story: {str(e)}")

    proactive_story = agent.proactive_story()
    return render_template('index.html', proactive_story=proactive_story)

@app.route('/results', methods=['POST'])
def results():
    story_id = request.form.get('story_id')
    submitted_story = request.form.get('story')

    if not story_id or not submitted_story:
        return render_template('index.html', error="Missing story details.")

    story_text = None
    try:
        with open("memory.json", "r") as f:
            memory = json.load(f)
            stories = memory.get("stories", [])
            for entry in stories:
                if entry.get("id") == story_id:
                    story_text = entry.get("story")
                    break
    except Exception as e:
        print("Error loading memory.json:", e)

    if not story_text:
        print("Story ID not found in memory.json. Falling back to submitted story.")
        story_text = submitted_story

    segments = story_text.split(". ")
    images = []
    audio_file = f"static/audio/{story_id}.mp3"
    os.makedirs("static/audio", exist_ok=True)

    for segment in segments:
        try:
            response = requests.post(
                "https://api.deepai.org/api/text2img",
                data={"text": segment},
                headers={"api-key": IMAGE_API_KEY}
            )
            image_url = response.json().get("output_url", "")
            if image_url:
                images.append(image_url)
        except Exception as e:
            print(f"Error generating image for segment '{segment}': {str(e)}")

    try:
        try:
            response = requests.post("http://localhost:5001/tts", json={"text": story_text})
            if response.status_code == 200:
                with open(audio_file, "wb") as f:
                    f.write(response.content)
                print("Audio generated using the open source TTS API.")
            else:
                print("Open source TTS API call failed with status:", response.status_code)
                raise Exception("Open source TTS API call failed")
        except Exception as e:
            print("Exception calling open source TTS API:", e)
            from gtts import gTTS
            tts = gTTS(text=story_text, lang="en")
            tts.save(audio_file)
            print("Audio generated using gTTS fallback.")
    except Exception as e:
        return render_template('index.html', error=f"Error generating audio: {str(e)}")

    return render_template('results.html', images=images, audio_file=audio_file, slide_count=len(images))

if __name__ == '__main__':
    app.run(debug=True)
