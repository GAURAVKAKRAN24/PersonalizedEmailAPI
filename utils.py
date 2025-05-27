from flask import jsonify as JSON
import json
import smtplib
from email.message import EmailMessage

def parse_and_validate_companies(company_email_list_str):
    try:
        companies = json.loads(company_email_list_str)
        if not isinstance(companies, list) or len(companies) == 0:
            return None, (JSON({"error": "company_email_list must be a non-empty JSON array"}), 400)
    except Exception as e:
        return None, (JSON({"error": "Invalid JSON in company_email_list", "details": str(e)}), 400)

    for i, entry in enumerate(companies):
        if not isinstance(entry, dict) or 'company' not in entry or 'email' not in entry:
            return None, (JSON({"error": f"Entry at index {i} must have 'company' and 'email' keys"}), 400)
    return companies, None

def user_authentication(email_user, email_pass):
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_user, email_pass)
        return None
    except smtplib.SMTPAuthenticationError:
        return JSON({"error": "Invalid sender email or password"}), 401
    except Exception as e:
        return JSON({"error": str(e)}), 500

def send_bulk_emails(email_user, email_pass, subject, body, companies, attachment_path, file_name):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_user, email_pass)
        for entry in companies:
            msg = EmailMessage()
            msg['Subject'] = subject.replace('{company}', entry['company'])
            msg['From'] = email_user
            msg['To'] = entry['email']
            msg.set_content(body.replace('{company}', entry['company']))

            if attachment_path:
                with open(attachment_path, 'rb') as f:
                    file_data = f.read()
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

            smtp.send_message(msg)