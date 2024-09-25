from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
import google.generativeai as genai
from requests import Session
from config.config import Config
from config.db import User, get_db

# Initialize the Generative AI model
genai.configure(api_key=Config.API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

ai_bp = Blueprint('ai', __name__)


def token_required(fn):
    """
    Decorator to enforce JWT authentication on routes.

    Args:
        fn: The original function to be wrapped.

    Returns:
        The wrapped function with authentication check.
    """
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Access the database session
        db: Session = next(get_db())
        # Get the current user's ID from the token
        current_user_id = get_jwt_identity()
        # Retrieve the user from the database
        current_user = db.query(User).filter_by(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found!"}), 403
        
        return fn(*args, **kwargs)
    return wrapper


@ai_bp.route('/analyze_cve', methods=['POST'])
@token_required
def analyze_cve():
    """
    Analyzes CVEs from the provided scan results and retrieves explanations and mitigation strategies
    from the Generative AI model.

    Returns:
        A JSON response containing the analysis results for each CVE.
    """
    responses = []
    data = request.json
    results = data.get('results', [])
     
    for result in results:
        severity = float(result.get('severity', 0))
        
        if severity > 0:
            cve_numbers = result.get('cve_numbers', [])
            description = result.get('description', 'No description available.')
            
            # If no CVE numbers are present, set to ["unknown"]
            if not cve_numbers:
                cve_numbers = ["unknown"]
            
            for cve in cve_numbers:
                if cve != "unknown":
                    # Query for known CVE numbers
                    query = (
                        f"I did a scan using OpenVAS and found a vulnerability with this CVE: {cve}. "
                        f"Details: {description}. "
                        "Can you explain this vulnerability and suggest mitigation steps? "
                        "If you can, add links for articles about this."
                    )
                else:
                    # Query for unknown CVE numbers
                    query = (
                        f"I did a scan using OpenVAS and found a vulnerability with the following details: {description}. "
                        "Can you provide more information about this vulnerability and suggest how to mitigate it? "
                        "If you can, add links for articles about this."
                    )
                
                # Get the response from the AI model
                try:
                    response = model.generate_content(query)
                    responses.append({
                        'cve': cve,
                        'answer': response.text if response else "No response from AI."
                    })
                except Exception as e:
                    responses.append({
                        'cve': cve,
                        'answer': f"Error processing CVE: {str(e)}"
                    })
    
    return jsonify(responses)
