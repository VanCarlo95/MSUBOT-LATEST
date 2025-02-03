


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from rasa.core.agent import Agent
# import asyncio
# import os
# import sys
# import glob
# import logging
# import tensorflow as tf

# # Suppress tensorflow logging
# tf.get_logger().setLevel('ERROR')
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# # Configure logging
# logging.basicConfig(level=logging.WARNING)

# app = Flask(__name__)
# CORS(app)

# def get_latest_model():
#     """Get the most recent model from the models directory"""
#     models_dir = 'models'
#     if not os.path.exists(models_dir):
#         os.makedirs(models_dir)
#         raise FileNotFoundError(f"Created new models directory at {models_dir}")
    
#     model_files = glob.glob(os.path.join(models_dir, '*.tar.gz'))
#     if not model_files:
#         raise FileNotFoundError(f"No model files found in {models_dir}")
    
#     latest_model = max(model_files, key=os.path.getmtime)
#     print(f"Loading model: {latest_model}")
#     return latest_model

# try:
#     model_path = get_latest_model()
#     agent = Agent.load(model_path)
#     print("Model loaded successfully!")
# except Exception as e:
#     print(f"Error loading model: {e}")
#     raise

# @app.route('/webhooks/rest/webhook', methods=['POST', 'OPTIONS'])
# async def webhook():
#     if request.method == 'OPTIONS':
#         return '', 204
        
#     try:
#         data = request.json
#         message = data.get('message')
#         sender_id = data.get('sender', 'default')
        
#         print(f"Received message: {message} from sender: {sender_id}")
        
#         if not message:
#             return jsonify({"error": "No message provided"}), 400
        
#         responses = await agent.handle_text(message)
#         print(f"Bot responses: {responses}")
        
#         formatted_responses = []
#         for response in responses:
#             if isinstance(response, dict) and 'text' in response:
#                 formatted_responses.append({
#                     'recipient_id': sender_id,
#                     'text': response['text']
#                 })
#             elif isinstance(response, str):
#                 formatted_responses.append({
#                     'recipient_id': sender_id,
#                     'text': response
#                 })
        
#         return jsonify(formatted_responses)
        
#     except Exception as e:
#         print(f"Error processing message: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({
#         "status": "healthy", 
#         "model": os.path.basename(model_path)
#     })

# if __name__ == '__main__':
#     cli = sys.modules['flask.cli']
#     cli.show_server_banner = lambda *x: None
#     print("\nRasa webhook server is running on http://localhost:5005")
#     app.run(port=5005, debug=False)




# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from rasa.core.agent import Agent
import asyncio
import os
import sys
import glob
import logging
import tensorflow as tf

# Suppress tensorflow logging
tf.get_logger().setLevel('ERROR')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Configure logging
logging.basicConfig(level=logging.WARNING)

app = Flask(__name__)

# Simple CORS configuration
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:8000", "http://127.0.0.1:8000", 
                        "http://localhost:5500", "http://127.0.0.1:5500"],  # Add more origins if needed
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Accept"],
             "max_age": 3600
         }
     })

def get_latest_model():
    models_dir = 'models'
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        raise FileNotFoundError(f"Created new models directory at {models_dir}")
    
    model_files = glob.glob(os.path.join(models_dir, '*.tar.gz'))
    if not model_files:
        raise FileNotFoundError(f"No model files found in {models_dir}")
    
    latest_model = max(model_files, key=os.path.getmtime)
    print(f"Loading model: {latest_model}")
    return latest_model

try:
    model_path = get_latest_model()
    agent = Agent.load(model_path)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

@app.route('/test', methods=['GET', 'OPTIONS'])
def test():
    return jsonify({"status": "ok"})

@app.route('/chat', methods=['POST', 'OPTIONS'])
async def chat():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        return response, 204
        
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        message = data.get('message')
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        sender_id = data.get('sender', 'default')
        print(f"Received message: {message} from sender: {sender_id}")
        
        # Get response from Rasa
        responses = await agent.handle_text(message)
        print(f"Bot responses: {responses}")
        
        # Combine all responses
        response_texts = []
        for response in responses:
            if isinstance(response, dict) and 'text' in response:
                response_texts.append(response['text'])
            elif isinstance(response, str):
                response_texts.append(response)
        
        # Join responses with appropriate formatting
        final_response = "\n\n".join(response_texts) if response_texts else "I'm not sure how to respond to that."
        
        return jsonify({
            'message': final_response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == '__main__':
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    print("\nRasa webhook server is running on http://localhost:5005")
    app.run(port=5005, debug=True)