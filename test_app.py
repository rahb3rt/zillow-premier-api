import json
from app import app  # Assuming the Flask app is named `app.py`, adjust the import as needed
import requests_mock

def test_login_endpoint():
    # Use the Flask test client
    client = app.test_client()

    # Mock the Zillow endpoint
    with requests_mock.Mocker() as m:
        m.post('https://www.zillow.com/user/account/services/Login.htm', text='mocked response')

        # Create test data
        data = {
            'username': '',
            'password': ''
        }

        # Send a request to the API
        response = client.post('/login', data=json.dumps(data), content_type='application/json')

        # Assert that the response status code is 200
        assert response.status_code == 200

        # Assert any other necessary conditions, e.g., response content, saved cookies, etc.
        json_data = json.loads(response.data)
        assert json_data['message'] == "Attempted login"

def test_search_contacts_no_email():
    client = app.test_client()

    # Mock the Zillow endpoint
    with requests_mock.Mocker() as m:
        mock_response = {
            "data": {
                "contacts": [
                    {
                        "contactId": "12345",
                        "emailAddresses": [{"email": "test1@example.com"}]
                    },
                    {
                        "contactId": "67890",
                        "emailAddresses": [{"email": "test2@example.com"}]
                    }
                ]
            }
        }
        m.get('https://premieragent.zillow.com/crm/proxy/contacts/activity/contacts/', json=mock_response)

        data = {'limit': 10}
        response = client.post('/search', data=json.dumps(data), content_type='application/json')

        assert response.status_code == 200
        assert json.loads(response.data) == ["test1@example.com", "test2@example.com"]

def test_search_contacts_with_email():
    client = app.test_client()

    # Mock the Zillow endpoint
    with requests_mock.Mocker() as m:
        mock_response = {
            "data": {
                "contacts": [
                    {
                        "contactId": "12345",
                        "emailAddresses": [{"email": "test1@example.com"}]
                    },
                    {
                        "contactId": "67890",
                        "emailAddresses": [{"email": "test2@example.com"}]
                    }
                ]
            }
        }
        m.get('https://premieragent.zillow.com/crm/proxy/contacts/activity/contacts/', json=mock_response)

        data = {'limit': 10, 'search_email': 'test1@example.com'}
        response = client.post('/search', data=json.dumps(data), content_type='application/json')

        assert response.status_code == 200
        assert json.loads(response.data) == ["12345"]


def test_get_csrf_token_success():
    client = app.test_client()

    # Mock the Zillow endpoint
    with requests_mock.Mocker() as m:
        mock_response_content = '<html><body><script>window.csrfToken = "test_token_1234";</script></body></html>'
        m.get('https://premieragent.zillow.com/crm/inbox/contacts', text=mock_response_content)

        response = client.get('/get_csrf_token')

        assert response.status_code == 200
        assert json.loads(response.data) == {"csrf_token": "test_token_1234"}

def test_get_csrf_token_failure():
    client = app.test_client()

    # Mock the Zillow endpoint without the CSRF token in the content
    with requests_mock.Mocker() as m:
        mock_response_content = '<html><body><script>window.somethingElse = "dummy_data";</script></body></html>'
        m.get('https://premieragent.zillow.com/crm/inbox/contacts', text=mock_response_content)

        response = client.get('/get_csrf_token')

        assert response.status_code == 404
        assert json.loads(response.data) == {"error": "CSRF token not found"}

