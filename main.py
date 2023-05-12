import run_autothesis
import run_classification
import json

if __name__ == "__main__":

    with open("settings.json", "r") as f:
        settings = json.load(f)

    print("\nRunning autothesis...")
    results = run_autothesis.run_autothesis(settings, check_for_existing_results=True)
    settings["3DThesis"]["results"] = results
    print(f"Output files: {results}")

    print("\nRunning classification...")
    result = run_classification.run_classification(settings)
    print(f"Output: {result}")