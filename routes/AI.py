from flask import Blueprint, request, jsonify
import google.generativeai as genai
from config.config import Config

# Initialize the Generative AI model
genai.configure(api_key=Config.API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/analyze_cve', methods=['POST'])
def analyze_cve():
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
                        "Can you explain this vulnerability and suggest mitigation steps?"
                        "if you can add links for articles about this."
                    )
                else:
                    # Query for unknown CVE numbers
                    query = (
                        f"I did a scan using OpenVAS and found a vulnerability with the following details: {description}. "
                        "Can you provide more information about this vulnerability and suggest how to mitigate it?"
                        "if you can add links for articles about this."
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
