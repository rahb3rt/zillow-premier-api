from flask import Flask, request, jsonify, url_for
import requests
import re

app = Flask(__name__)

ZILLOW_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

statuses = {
    500: "New",
    505: "Attempted Contact",
    510: "Spoke with Customer",
    515: "Appointment Sent",
    520: "Met with Customer",
    565: "Showing Homes",
    530: "Submitting Offer",
    545: "Under Contract",
    550: "Sale Closed",
    555: "Nurture",
    560: "Rejected"
}

@staticmethod
def get_contact_id(email, limit=200):
    url = 'http://127.0.0.1:5000' + url_for('search_contacts')
    payload = {
        "search_email": email,
        "limit": limit
    }

    contact_id_response = requests.post(url, json=payload)
    contact_id = contact_id_response.json()[0]
    return contact_id

@staticmethod
def get_csrf_token():
    url = 'http://127.0.0.01:5000' + url_for('get_token')
    csrf_token_response = requests.get(url)
    csrf_token = csrf_token_response.json()['csrf_token']
    return csrf_token

@staticmethod
def read_cookies_from_file():
    with open('cookies.txt', 'r') as f:
        cookies = {}
        for line in f:
            name, value = line.strip().split('=', 1)
            cookies[name] = value
    return cookies


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    headers = {
        **ZILLOW_HEADERS,
        'authority': 'www.zillow.com',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.zillow.com',
        'referer': 'https://www.zillow.com/user/account/ZillowLogin.htm?client_id=PAClient&continue=https://authv2.zillow.com:443/externalLogin?nonce=7hOeM8&force_display_login=true&hashing=287ad8ac12757c8cf8411e0225c6f821&nonce=7hOeM8',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }

    data = {
        'ap': 'undefined',
        'authToken': '',
        'email': username,
        'password': password,
        'destination': 'PAClient',
        'createPasswordContinueUrl': 'null',
    }
    
    cookies = {'INSERT_YOUR_COOKIE_NAME_HERE': 'INSERT_YOUR_COOKIE_STRING_HERE'}
    
    response = requests.post(
        'https://www.zillow.com/user/account/services/Login.htm',
        headers=headers,
        data=data,
        cookies=cookies
    )
    
    with open('cookies.txt', 'w') as f:
        for cookie in response.cookies:
            f.write(f"{cookie.name}={cookie.value}\n")

    return jsonify({"message": "Attempted login"}), 200


@app.route('/search', methods=['POST'])
def search_contacts():
    limit = request.json.get('limit')
    search_email = request.json.get('search_email')
    offset = 0
    
    headers = {
        **ZILLOW_HEADERS,
        'authority': 'premieragent.zillow.com',
        'referer': 'https://premieragent.zillow.com/crm/inbox/contacts',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }

    cookies = read_cookies_from_file()
    
    response = requests.get(
        f'https://premieragent.zillow.com/crm/proxy/contacts/activity/contacts/?limit={limit}&offset={offset}&sortField=lastActivityDate&sortDirection=desc',
        headers=headers,
        cookies=cookies
    )
    
    data = response.json()

    if not search_email:
        emails = [email['email'] for contact in data['data']['contacts'] for email in contact.get('emailAddresses', [])]
        return jsonify(emails), 200

    contact_ids = [contact['contactId'] for contact in data['data']['contacts'] if any(email['email'] == search_email for email in contact.get('emailAddresses', []))]
    return jsonify(contact_ids), 200


@app.route('/get_csrf_token', methods=['GET'])
def get_token():
    headers = {
        **ZILLOW_HEADERS,
        'authority': 'premieragent.zillow.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'cache-control': 'max-age=0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    }

    cookies = read_cookies_from_file()

    response = requests.get(
        'https://premieragent.zillow.com/crm/inbox/contacts',
        headers=headers,
        cookies=cookies
    )

    match = re.search(r'window.csrfToken = "(.*?)"', response.text)
    if match:
        csrf_token = match.group(1)
        return jsonify({"csrf_token": csrf_token}), 200
    else:
        return jsonify({"error": "CSRF token not found"}), 404


@app.route('/contact_details', methods=['GET'])
def get_contact_details():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    contact_id = get_contact_id(email)

    if not contact_id:
        return jsonify({"error": f"No contact found for email {email}"}), 404

    csrf_token = get_csrf_token()

    headers = {
        **ZILLOW_HEADERS,
        'authority': 'premieragent.zillow.com',
        'referer': f'https://premieragent.zillow.com/crm/contacts/contactdetails/{contact_id}/properties',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-csrf-token': csrf_token
    }

    cookies = read_cookies_from_file()
    
    response = requests.get(
        f'https://premieragent.zillow.com/crm/proxy/contacts/contacts/{contact_id}',
        headers=headers,
        cookies=cookies
    )

    return jsonify(response.json()), response.status_code


@app.route('/contact_history', methods=['GET'])
def get_contact_history():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    contact_id = get_contact_id(email)
    
    if not contact_id:
        return jsonify({"error": f"No contact found for email {email}"}), 404

    headers = {
        **ZILLOW_HEADERS,
        'authority': 'premieragent.zillow.com',
        'referer': f'https://premieragent.zillow.com/crm/contacts/contactdetails/{contact_id}/history',
    }

    cookies = read_cookies_from_file()

    response = requests.get(
        f'https://premieragent.zillow.com/crm/contacts/{contact_id}/history',
        headers=headers,
        cookies=cookies
    )

    return jsonify(response.json()), response.status_code


@app.route('/get_contact_notes', methods=['GET'])
def fetch_contact_notes():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    contact_id = get_contact_id(email)
    if not contact_id:
        return jsonify({"error": f"No contact found for email {email}"}), 404

    # Make an HTTP request to fetch the notes for the contact.
    url = f"https://premieragent.zillow.com/crm/proxy/contacts/contacts/{contact_id}/notes"
    headers = {
        **ZILLOW_HEADERS,
        'authority': 'premieragent.zillow.com',
        'referer': 'https://premieragent.zillow.com/crm/inbox/contacts',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }
    # Assuming cookies.txt has one cookie per line in the format: "name=value"
    cookies = read_cookies_from_file()
    response = requests.get(url, headers=headers, cookies=cookies)

    return jsonify(response.json()), response.status_code


@app.route('/add_contact_note', methods=['POST'])
def add_contact_note():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    contact_id = get_contact_id(email)
    if not contact_id:
        return jsonify({"error": f"No contact found for email {email}"}), 404

    csrf = get_csrf_token()
    cookies = read_cookies_from_file()

    # Parse JSON data from request
    try:
        json_data = request.json
    except:
        return jsonify({"error": "Invalid JSON data provided"}), 400

    headers = {
        **ZILLOW_HEADERS,
        'authority': 'premieragent.zillow.com',
        'content-type': 'application/json',
        'referer': f'https://premieragent.zillow.com/crm/contacts/contactdetails/{contact_id}/notes',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-csrf-token': csrf
    }

    response = requests.post(
        f"https://premieragent.zillow.com/crm/proxy/contacts/contacts/{contact_id}/notes",
        headers=headers,
        json=json_data,
        cookies=cookies
    )

    return jsonify(response.json()), response.status_code



@app.route('/update-contact-status', methods=['POST'])
def update_contact_status():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    contact_id = get_contact_id(email)
    if not contact_id:
        return jsonify({"error": f"No contact found for email {email}"}), 404

    csrf = get_csrf_token()
    cookies = read_cookies_from_file()

    # Parse JSON data from request
    try:
        json_data = request.json
        if "statusId" not in json_data:
            return jsonify({"error": "statusId is required in the JSON payload"}), 400
        # Ensure that the provided statusId is valid
        if json_data["statusId"] not in statuses:
            return jsonify({"error": f"Invalid statusId. Valid values are: {', '.join(map(str, statuses.keys()))}"}), 400
    except:
        return jsonify({"error": "Invalid JSON data provided"}), 400

    headers = {
        **ZILLOW_HEADERS,
        'authority': 'premieragent.zillow.com',
        'content-type': 'application/json',
        'referer': f'https://premieragent.zillow.com/crm/contacts/contactdetails/{contact_id}/notes',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-csrf-token': csrf
    }

    response = requests.put(
        f"https://premieragent.zillow.com/crm/proxy/contacts/contacts/{contact_id}/status",
        headers=headers,
        json=json_data,
        cookies=cookies
    )

    return jsonify(response.json()), response.status_code


if __name__ == '__main__':
    app.run(debug=True)
