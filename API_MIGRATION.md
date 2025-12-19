# API Migration Guide

## Breaking Changes in Latest Version

### Overview
This release includes breaking changes to improve API security and consistency. Both the signup and unregister endpoints now use request bodies instead of query parameters for email addresses.

### Why These Changes?
1. **Security**: Email addresses in query parameters appear in server logs, which is a security concern
2. **RESTful Best Practices**: POST and DELETE requests with data should use request bodies
3. **Consistency**: Both endpoints now follow the same pattern
4. **Email Validation**: Added automatic email format validation using Pydantic's EmailStr

---

## Affected Endpoints

### 1. POST /activities/{activity_name}/signup

**BEFORE:**
```http
POST /activities/Chess%20Club/signup?email=student@mergington.edu
```

**AFTER:**
```http
POST /activities/Chess%20Club/signup
Content-Type: application/json

{
  "email": "student@mergington.edu"
}
```

**Migration Steps:**
1. Add `Content-Type: application/json` header to your requests
2. Move the email parameter from query string to JSON request body
3. Ensure email addresses are valid (will now return 422 for invalid formats)

**JavaScript Example:**
```javascript
// Before
fetch(`/activities/${activity}/signup?email=${email}`, {
  method: 'POST'
});

// After
fetch(`/activities/${activity}/signup`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ email: email })
});
```

---

### 2. DELETE /activities/{activity_name}/unregister

**BEFORE:**
```http
DELETE /activities/Chess%20Club/unregister?email=student@mergington.edu
```

**AFTER:**
```http
DELETE /activities/Chess%20Club/unregister
Content-Type: application/json

{
  "email": "student@mergington.edu"
}
```

**Migration Steps:**
1. Add `Content-Type: application/json` header to your requests
2. Move the email parameter from query string to JSON request body
3. Ensure email addresses are valid (will now return 422 for invalid formats)

**JavaScript Example:**
```javascript
// Before
fetch(`/activities/${activity}/unregister?email=${email}`, {
  method: 'DELETE'
});

// After
fetch(`/activities/${activity}/unregister`, {
  method: 'DELETE',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ email: email })
});
```

---

## Error Code Changes

### New Error Code: 422 Unprocessable Entity
Both endpoints will now return HTTP 422 if the email format is invalid.

**Example Error Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "not-an-email"
    }
  ]
}
```

---

## Testing Your Migration

### Python/pytest Example:
```python
# Before
response = client.post("/activities/Chess Club/signup?email=student@example.com")

# After
response = client.post(
    "/activities/Chess Club/signup",
    json={"email": "student@example.com"}
)
```

### cURL Examples:

**Signup:**
```bash
# Before
curl -X POST "http://localhost:8000/activities/Chess%20Club/signup?email=student@mergington.edu"

# After
curl -X POST "http://localhost:8000/activities/Chess%20Club/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "student@mergington.edu"}'
```

**Unregister:**
```bash
# Before
curl -X DELETE "http://localhost:8000/activities/Chess%20Club/unregister?email=student@mergington.edu"

# After
curl -X DELETE "http://localhost:8000/activities/Chess%20Club/unregister" \
  -H "Content-Type: application/json" \
  -d '{"email": "student@mergington.edu"}'
```

---

## Timeline

- **Deprecation Notice**: N/A (breaking change introduced immediately)
- **Removal Date**: Old query parameter format is no longer supported

---

## Need Help?

If you encounter issues during migration, please:
1. Verify your request includes the `Content-Type: application/json` header
2. Ensure email addresses are valid
3. Check that the email is in the request body, not query parameters
4. Refer to the updated API documentation or tests in the repository

---

## Additional Resources

- See `tests/test_app.py` for complete test examples
- See `src/static/app.js` for frontend implementation examples
- FastAPI will provide detailed error messages for validation errors
