from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import os
import tempfile
import json

app = Flask(__name__)
CORS(app)

EMAIL_USER = 'gauravkakran24@gmail.com'       # replace with your email
EMAIL_PASS = 'bdpsxfnvxeewivls'           # replace with your app password

@app.route('/send-emails', methods=['POST'])
def send_emails():
    # Read form fields (for multipart/form-data)
    subject = request.form.get('subject')
    body = request.form.get('body')
    company_email_list_str = request.form.get('company_email_list')
    file = request.files.get('file')

    # Validate required fields
    if not subject or not body or not company_email_list_str:
        return jsonify({"error": "Missing required fields: subject, body or company_email_list"}), 400

    # Parse company_email_list JSON string to Python list
    try:
        companies = json.loads(company_email_list_str)
        if not isinstance(companies, list) or len(companies) == 0:
            return jsonify({"error": "company_email_list must be a non-empty JSON array"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid JSON in company_email_list", "details": str(e)}), 400

    # Validate each entry
    for i, entry in enumerate(companies):
        if not isinstance(entry, dict) or 'company' not in entry or 'email' not in entry:
            return jsonify({"error": f"Entry at index {i} must have 'company' and 'email' keys"}), 400

    # Save file temporarily if provided
    attachment_path = None
    file_name = None
    if file:
        temp = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp.name)
        temp.close()
        attachment_path = temp.name
        file_name = file.filename

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            for entry in companies:
                msg = EmailMessage()
                msg['Subject'] = subject.replace('{company}', entry['company'])
                msg['From'] = EMAIL_USER
                msg['To'] = entry['email']
                msg.set_content(body.replace('{company}', entry['company']))

                if attachment_path:
                    with open(attachment_path, 'rb') as f:
                        file_data = f.read()
                    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

                smtp.send_message(msg)

        return jsonify({'message': 'Emails sent successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)

if __name__ == '__main__':
    app.run(debug=True)
