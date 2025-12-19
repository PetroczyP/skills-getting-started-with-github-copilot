# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Unregister from activities
- **Multi-language support** (English and Hungarian)
- Language switching with flag icons

## Multi-Language Support

The application now supports both English and Hungarian languages:

### Frontend Language Switching

- Click on the **🇬🇧 (English)** or **🇭🇺 (Hungarian)** flag buttons in the header to switch languages
- Language preference is saved in browser localStorage
- The page will not reload if you click on the currently active language
- All UI text, activity names, descriptions, and messages are translated

### Supported Languages

- **English (en)** - Default language
- **Hungarian (hu)** - Magyar nyelv

### What Gets Translated

1. **UI Elements:**
   - Header text (school name, page title)
   - Form labels and placeholders
   - Button text
   - Loading and error messages
   - Confirmation dialogs

2. **Activity Content:**
   - Activity names
   - Activity descriptions
   - Schedule information

3. **API Response Messages:**
   - Success messages (signup, unregister)
   - User-facing error messages

**Note:** System-level errors and backend logs remain in English for technical consistency.

## Getting Started

1. Install the dependencies:

   ```bash
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```bash
   python app.py
   ```

3. Open your browser and go to:
   - Web application: http://localhost:8000/
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities?lang={lang}`                                         | Get all activities with their details in specified language (en/hu) |
| POST   | `/activities/{activity_name}/signup?email={email}&lang={lang}`    | Sign up for an activity with localized response messages            |
| DELETE | `/activities/{activity_name}/unregister?email={email}&lang={lang}`| Unregister from an activity with localized response messages        |

### Query Parameters

- `lang` (optional): Language code - `en` for English or `hu` for Hungarian (default: `en`)
- `email` (required): Student's email address

### Example API Calls

**English:**
```bash
GET /activities?lang=en
POST /activities/Chess%20Club/signup?email=student@mergington.edu&lang=en
DELETE /activities/Chess%20Club/unregister?email=student@mergington.edu&lang=en
```

**Hungarian:**
```bash
GET /activities?lang=hu
POST /activities/Sakk%20Klub/signup?email=student@mergington.edu&lang=hu
DELETE /activities/Sakk%20Klub/unregister?email=student@mergington.edu&lang=hu
```

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description (translated per language)
   - Schedule (translated per language)
   - Maximum number of participants allowed
   - List of student emails who are signed up (shared across languages)

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts. **Participant lists are synchronized across both language versions** - a student signed up in English will also appear in the Hungarian version.

## Technical Details

### Language Implementation

- **Frontend:** JavaScript translation dictionaries with localStorage persistence
- **Backend:** Python dictionaries for English and Hungarian activity data
- **Participant Storage:** Shared storage ensuring consistency across languages
- **Activity Name Mapping:** Bidirectional mapping between English and Hungarian activity names

## Testing

Run the test suite with:

```bash
pytest
```

The test suite includes tests for:
- Language-specific API responses
- Participant synchronization across languages
- Localized error messages
- Capacity enforcement for both languages
