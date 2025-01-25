# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from rasa.core.agent import Agent
# import asyncio

# app = Flask(__name__)
# CORS(app)

# model_path = 'models/20250109-222450-boxy-cost.tar.gz'
# agent = Agent.load(model_path)

# @app.route('/chat', methods=['POST'])
# async def chat():
#     message = request.json['message']
#     responses = await agent.handle_text(message)
#     return jsonify(responses)

# if __name__ == '__main__':
#     asyncio.run(app.run(port=5005))




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

# # Configure logging to show only warnings and errors
# logging.basicConfig(
#     level=logging.WARNING,
#     format='%(levelname)s: %(message)s'
# )

# # Suppress unnecessary logs
# logging.getLogger('werkzeug').setLevel(logging.ERROR)
# logging.getLogger('rasa').setLevel(logging.WARNING)

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

# @app.route('/chat', methods=['POST'])
# async def chat():
#     try:
#         message = request.json.get('message')
        
#         if not message:
#             return jsonify({"error": "No message provided"}), 400
        
#         responses = await agent.handle_text(message)
        
#         # Format the response properly
#         formatted_responses = []
#         for response in responses:
#             if isinstance(response, dict) and 'text' in response:
#                 formatted_responses.append({
#                     'text': response['text']
#                 })
#             elif isinstance(response, str):
#                 formatted_responses.append({
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
#     # Disable Flask development server banner
#     cli = sys.modules['flask.cli']
#     cli.show_server_banner = lambda *x: None
    
#     print("Server is running on http://localhost:5005")
#     app.run(port=5005, debug=False)












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
# Configure CORS properly
CORS(app, resources={
    r"/chat": {
        "origins": ["http://localhost:8000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/health": {
        "origins": ["http://localhost:8000"],
        "methods": ["GET"]
    }
})

def get_latest_model():
    """Get the most recent model from the models directory"""
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

@app.route('/chat', methods=['POST', 'OPTIONS'])
async def chat():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        message = request.json.get('message')
        print(f"Received message: {message}")
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        responses = await agent.handle_text(message)
        print(f"Bot responses: {responses}")
        
        # Format the response properly
        formatted_responses = []
        for response in responses:
            if isinstance(response, dict) and 'text' in response:
                formatted_responses.append({
                    'text': response['text']
                })
            elif isinstance(response, str):
                formatted_responses.append({
                    'text': response
                })
        
        return jsonify(formatted_responses)
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "model": os.path.basename(model_path)
    })

if __name__ == '__main__':
    # Disable Flask development server banner
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    
    print("\nServer is running on http://localhost:5005")
    app.run(port=5005, debug=False, host='0.0.0.0')