import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

SUBMISSIONS_FILE = 'submissions.json'


def load_submissions():
    if not os.path.exists(SUBMISSIONS_FILE):
        return []
    with open(SUBMISSIONS_FILE, 'r') as f:
        return json.load(f)


def save_submissions(submissions):
    with open(SUBMISSIONS_FILE, 'w') as f:
        json.dump(submissions, f, indent=2)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    required = ['name', 'email', 'phone', 'street', 'city', 'state', 'zip', 'notes']
    missing = [f for f in required if not data.get(f, '').strip()]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    entry = {
        'id': datetime.utcnow().strftime('%Y%m%d%H%M%S%f'),
        'submitted_at': datetime.utcnow().isoformat() + 'Z',
        'name': data['name'].strip(),
        'email': data['email'].strip(),
        'phone': data['phone'].strip(),
        'address': {
            'street': data['street'].strip(),
            'city': data['city'].strip(),
            'state': data['state'].strip(),
            'zip': data['zip'].strip(),
        },
        'notes': data['notes'].strip(),
    }

    submissions = load_submissions()
    submissions.append(entry)
    save_submissions(submissions)

    print(f"[{entry['submitted_at']}] New submission from {entry['name']} ({entry['email']})")
    return jsonify({'message': 'Submission received successfully.'}), 201


@app.route('/submissions', methods=['GET'])
def get_submissions():
    return jsonify(load_submissions())


@app.route('/submissions/<submission_id>', methods=['DELETE'])
def delete_submission(submission_id):
    submissions = load_submissions()
    updated = [s for s in submissions if s['id'] != submission_id]
    if len(updated) == len(submissions):
        return jsonify({'error': 'Submission not found.'}), 404
    save_submissions(updated)
    return jsonify({'message': 'Submission deleted.'})


if __name__ == '__main__':
    app.run(debug=True, port=8080)
