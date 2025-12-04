from flask import Flask, render_template, request
import joblib
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# We need to go up one level (..) to find the model_training folder
MODEL_PATH = '../model_training/bug_predictor.pkl'

# Load the Model (with error handling)
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded successfully from {MODEL_PATH}")
    else:
        model = None
        print(f"⚠️ WARNING: Model not found at {MODEL_PATH}. Run train_model.py first!")
except Exception as e:
    model = None
    print(f"❌ Error loading model: {e}")

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    
    if request.method == 'POST':
        # Check if model is loaded
        if not model:
            return render_template('index.html', error="Model not loaded. Please contact the administrator.")

        # Get the uploaded files
        uploaded_files = request.files.getlist('project_files')
        
        for file in uploaded_files:
            if file.filename == '': continue
            
            try:
                # Read file content (decode bytes to string)
                code_content = file.read().decode('utf-8', errors='ignore')
                
                # PREDICT
                # The model returns 0 (Clean) or 1 (Defective)
                prediction = model.predict([code_content])[0]
                probability = model.predict_proba([code_content])[0][1] # Probability of being '1'
                
                # Format the result for the UI
                status = "RISKY" if prediction == 1 else "SAFE"
                css_class = "danger" if prediction == 1 else "success"
                
                results.append({
                    'filename': file.filename,
                    'status': status,
                    'probability': round(probability * 100, 2),
                    'css_class': css_class
                })
            except Exception as e:
                print(f"Error processing {file.filename}: {e}")

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)