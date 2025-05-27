from flask import request, jsonify
from utils import parse_and_validate_companies, send_bulk_emails, user_authentication
from scheduler import schedule_email_job
import tempfile
import os
from datetime import datetime, timedelta

def register_routes(app, scheduler):
    @app.route('/send-emails', methods=['POST'])
    def send_emails():
        EMAIL_USER = request.form.get('senderGmail')
        EMAIL_PASS = request.form.get('password')
        subject = request.form.get('subject')
        body = request.form.get('body')
        company_email_list_str = request.form.get('companies')
        file = request.files.get('file')
        schedule_time = request.form.get('schedule_time')  # Format: "HH:MM"

        auth_error = user_authentication(EMAIL_USER, EMAIL_PASS)
        if auth_error:
            return auth_error

        if not EMAIL_USER or not EMAIL_PASS:
            return jsonify({"error": "Missing required fields: senderGmail or password"}), 400

        if not subject or not body or not company_email_list_str:
            return jsonify({"error": "Missing required fields: subject, body or company_email_list"}), 400

        companies, error_response = parse_and_validate_companies(company_email_list_str)
        if error_response:
            return error_response

        attachment_path = None
        file_name = None
        if file:
            temp = tempfile.NamedTemporaryFile(delete=False)
            file.save(temp.name)
            temp.close()
            attachment_path = temp.name
            file_name = file.filename

        if schedule_time:
            job_id = f"email_job_{EMAIL_USER}_{schedule_time.replace(':', '_')}"
            schedule_email_job(
                scheduler, job_id, schedule_time,
                EMAIL_USER, EMAIL_PASS, subject, body, companies, attachment_path, file_name
            )
            schedule_time_formatted = datetime.fromisoformat(schedule_time).strftime("%B %d, %Y at %I:%M %p")
            print()
            return jsonify({"message": f"Email scheduled at {schedule_time_formatted}"})
        else:
            try:
                send_bulk_emails(
                    EMAIL_USER, EMAIL_PASS, subject, body, companies, attachment_path, file_name
                )
                return jsonify({'message': 'Emails sent successfully'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            finally:
                if attachment_path and os.path.exists(attachment_path):
                    os.remove(attachment_path)