from flask import Flask, render_template, request
from agent import FairyTaleAgent

app = Flask(__name__)
agent = FairyTaleAgent()

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

if __name__ == '__main__':
    app.run(debug=True)