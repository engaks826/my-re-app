from flask import Flask, request, render_template
import pandas as pd
import os
from model import load_model, predict, recommend_from_frequency, retrain_model
from github_sync import sync_with_github, pull_only

# --- Configuration ---
REPO_PATH = os.getenv("GIT_REPO_PATH", ".")
FEEDBACK_FILE = "user_feedback.csv"

app = Flask(__name__)

model = None  # lazy-loaded model

def init_model():
    global model
    pull_only(REPO_PATH)
    model = load_model(os.path.join(REPO_PATH, FEEDBACK_FILE))

@app.route("/", methods=["GET", "POST"])
def index():
    global model
    if model is None:
        init_model()

    prediction = None
    recommendations = []
    message = ""

    if request.method == "POST":
        try:
            f1 = float(request.form["feature1"])
            f2 = float(request.form["feature2"])

            if "corrected_label" in request.form:
                corrected = float(request.form["corrected_label"])
                file_path = os.path.join(REPO_PATH, FEEDBACK_FILE)

                df = pd.read_csv(file_path)
                new_row = pd.DataFrame([{
                    "feature1": f1,
                    "feature2": f2,
                    "label": corrected,
                    "frequency": 1
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(file_path, index=False)

                sync_with_github(REPO_PATH, FEEDBACK_FILE)

                model = retrain_model(file_path)

                message = "✅ Feedback saved, synced, and model retrained."
            else:
                prediction = predict(model, f1, f2)
                recommendations = recommend_from_frequency(os.path.join(REPO_PATH, FEEDBACK_FILE), f1, f2)

        except Exception as e:
            message = f"❌ Error: {e}"

    return render_template("index.html",
                           prediction=prediction,
                           recommendations=recommendations,
                           message=message)


if __name__ == "__main__":
    app.run(debug=True)
