## Flask Zillow API Wrapper

This code represents a Flask application that wraps around Zillow's internal APIs. It's meant to demonstrate how you can interact with Zillow APIs for various functionalities.

### Dependencies:
- Flask
- requests
- re

### ZILLOW_HEADERS
This dictionary contains headers used in various requests to Zillow. It's important for mimicking the request as if it was made from a legitimate browser.

### statuses
A dictionary that maps status codes to human-readable status messages.

---

### 
This function retrieves the contact ID associated with an email address.
- **Parameters**:
  - : Email of the contact.
  - : Maximum number of results to return.
- **Returns**: The contact ID associated with the email.

---

### 
Retrieves the CSRF token required for authenticated requests.
- **Returns**: CSRF token.

---

### 
Reads cookies from a file and returns them in a dictionary format.
- **Returns**: A dictionary containing cookie name-value pairs.

---

### 
Endpoint to log into Zillow. After successful login, it saves the cookies received in a file.
- **Returns**: JSON response with a message indicating the login attempt.

---

### 
Endpoint to search for contacts on Zillow based on email or fetch all emails.
- **Returns**: A list of emails or contact IDs based on the provided search criteria.

---

### 
Endpoint to get CSRF token from Zillow.
- **Returns**: CSRF token or an error if not found.

---

### 
Endpoint to get the details of a contact based on their email.
- **Returns**: Contact details or an error message.

---

### 
Endpoint to get the interaction history of a contact based on their email.
- **Returns**: Contact's interaction history or an error message.

---

### 
Endpoint to fetch notes associated with a contact based on their email.
- **Returns**: Contact's notes or an error message.

---

### 
Endpoint to add a note to a contact's record.
- **Returns**: Response after adding the note or an error message.

---

### 
Endpoint to update the status of a contact.
- **Returns**: Response after updating the status or an error message.

---

### Main Execution
The Flask application runs with debug mode enabled.

---

Note: For actual deployment, consider using a production-ready server like Gunicorn and remember to disable the debug mode.

