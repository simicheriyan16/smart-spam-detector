from flask import Flask, render_template, request, jsonify
import pickle
from datetime import datetime
import re

app = Flask(__name__)

print("\n🚀 Loading spam detection model...")
try:
    classifier = pickle.load(open('spam_classifier.pkl', 'rb'))
    vectorizer = pickle.load(open('tfidf_extractor.pkl', 'rb'))
    print("✅ Model loaded successfully!\n")
except FileNotFoundError:
    print("❌ Error: Model files not found. Run 'python engine.py' first.\n")
    exit()

# In-memory message history
message_history = []

def analyze_message_content(text):
    """Extract message characteristics"""
    return {
        'word_count': len(text.split()),
        'char_count': len(text),
        'has_urls': bool(re.search(r'http|www', text)),
        'has_numbers': bool(re.search(r'\d', text)),
        'has_caps': bool(re.search(r'[A-Z]{2,}', text))
    }

def classify_message(text):
    """Classify message using trained model"""
    if not text or len(text.strip()) < 3:
        return None
    
    message_vector = vectorizer.transform([text])
    prediction = classifier.predict(message_vector)[0]
    decision_score = classifier.decision_function(message_vector)[0]
    
    spam_probability = abs(decision_score) / (1 + abs(decision_score))
    if prediction == 'ham':
        spam_probability = 1 - spam_probability
    
    return {
        'classification': 'SPAM' if prediction == 'spam' else 'LEGITIMATE',
        'emoji': '⚠️ SPAM' if prediction == 'spam' else '✅ SAFE',
        'risk_level': round(spam_probability * 100, 2),
        'is_spam': prediction == 'spam',
        'details': analyze_message_content(text)
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    classification = None
    error_msg = None
    message_text = ''
    
    if request.method == 'POST':
        message_text = request.form.get('sms_input', '').strip()
        
        if not message_text:
            error_msg = '⚠️ Please enter a message to analyze'
        elif len(message_text) < 3:
            error_msg = '⚠️ Message must be at least 3 characters'
        elif len(message_text) > 1000:
            error_msg = '⚠️ Message is too long (max 1000 characters)'
        else:
            result = classify_message(message_text)
            if result:
                classification = result
                message_history.append({
                    'text': message_text[:60] + '...' if len(message_text) > 60 else message_text,
                    'result': result['classification'],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
    
    return render_template(
        'dashboard.html',
        classification=classification,
        error=error_msg,
        input_text=message_text,
        history=message_history[-8:]
    )

@app.route('/api/check', methods=['POST'])
def api_check():
    """REST API endpoint for message classification"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message field is required'}), 400
        
        if len(message) < 3:
            return jsonify({'error': 'Message too short'}), 400
        
        result = classify_message(message)
        if not result:
            return jsonify({'error': 'Classification failed'}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def api_history():
    """Get analysis history"""
    return jsonify({'total_analyzed': len(message_history), 'recent': message_history[-10:]})

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get statistics"""
    if not message_history:
        return jsonify({'spam_count': 0, 'safe_count': 0, 'total': 0, 'spam_rate': 0})
    
    spam_count = sum(1 for m in message_history if m['result'] == 'SPAM')
    safe_count = len(message_history) - spam_count
    
    return jsonify({
        'total': len(message_history),
        'spam_count': spam_count,
        'safe_count': safe_count,
        'spam_rate': round((spam_count / len(message_history)) * 100, 2)
    })

if __name__ == '__main__':
    print("📧 Spam Detection Service Starting...")
    print("📍 Open: http://localhost:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
