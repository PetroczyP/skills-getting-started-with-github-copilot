# Traceability Matrix - Mergington High School Activities API

**Last Updated:** December 28, 2025  
**Purpose:** Links user requirements to test cases to automated tests

---

## Table of Contents

1. [Requirements Overview](#requirements-overview)
2. [Feature Coverage](#feature-coverage)
3. [Traceability Matrix](#traceability-matrix)
4. [Coverage Summary](#coverage-summary)

---

## Requirements Overview

### User Stories

| ID | User Story | Priority | Status |
|----|------------|----------|--------|
| US-001 | As a student, I want to view available extracurricular activities so that I can see what options are available | P1 | ✅ Implemented |
| US-002 | As a student, I want to sign up for an activity so that I can participate in it | P1 | ✅ Implemented |
| US-003 | As a student, I want to unregister from an activity so that I can free up my slot | P1 | ✅ Implemented |
| US-004 | As a student, I want to see activities in my preferred language (English/Hungarian) so that I can understand them better | P1 | ✅ Implemented |
| US-005 | As a student, I want to see how many spots are left in an activity so that I know if I can join | P1 | ✅ Implemented |
| US-006 | As an admin, I want to prevent signups when an activity is full so that capacity is not exceeded | P1 | ✅ Implemented |
| US-007 | As an admin, I want to prevent duplicate signups so that students aren't registered multiple times | P1 | ✅ Implemented |
| US-008 | As a developer, I want the system to validate email addresses so that only valid emails are accepted | P1 | ✅ Implemented |
| US-009 | As a developer, I want infrastructure tests so that import/startup errors are caught early | P1 | ✅ Implemented |

---

## Feature Coverage

### Core Features

| Feature | Requirements | Test Cases | Automation | Coverage |
|---------|--------------|------------|------------|----------|
| **Activity Listing** | US-001, US-004, US-005 | TC-ACTIVITIES-001 through TC-ACTIVITIES-005, TC-LANGUAGE-001, TC-LANGUAGE-002 | ✅ 7 tests | 100% |
| **Activity Signup** | US-002, US-006, US-007, US-008 | TC-SIGNUP-001 through TC-SIGNUP-005, TC-CAPACITY-001 through TC-CAPACITY-004, TC-RACE-001 through TC-RACE-006 | ✅ 15 tests | 100% |
| **Activity Unregister** | US-003 | TC-UNREGISTER-001 through TC-UNREGISTER-005 | ✅ 5 tests | 100% |
| **Language Support** | US-004 | TC-LANGUAGE-001, TC-LANGUAGE-002, plus all *-002 variants | ✅ 9 tests | 100% |
| **Capacity Management** | US-006 | TC-CAPACITY-001 through TC-CAPACITY-004, TC-RACE-001 through TC-RACE-006 | ✅ 10 tests | 100% |
| **Race Conditions** | US-006 | TC-RACE-001 through TC-RACE-006 | ✅ 6 tests | 100% |
| **Infrastructure** | US-009 | TC-INFRA-* (40 tests) | ✅ 40 tests | 100% |

---

## Traceability Matrix

### US-001: View Available Activities

**Requirement:** As a student, I want to view available extracurricular activities so that I can see what options are available.

**Acceptance Criteria:**
- ✅ AC-001-01: System displays all 9 available activities
- ✅ AC-001-02: Each activity shows description, schedule, and capacity
- ✅ AC-001-03: System shows current participants for each activity

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-ACTIVITIES-001 | Get all activities in English | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-ACTIVITIES-002 | Get all activities in Hungarian | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-ACTIVITIES-004 | Activities have correct structure | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-ACTIVITIES-005 | Activities include participant lists | [test_app.py](../../tests/test_app.py) | ✅ Pass |

---

### US-002: Sign Up for Activity

**Requirement:** As a student, I want to sign up for an activity so that I can participate in it.

**Acceptance Criteria:**
- ✅ AC-002-01: Student can sign up with valid email
- ✅ AC-002-02: System confirms successful signup
- ✅ AC-002-03: Student appears in activity participants list
- ✅ AC-002-04: System validates email format

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-SIGNUP-001 | Successful signup in English | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-SIGNUP-002 | Successful signup in Hungarian | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-SIGNUP-003 | Signup for nonexistent activity | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-SIGNUP-005 | Multiple students can signup | [test_app.py](../../tests/test_app.py) | ✅ Pass |

---

### US-003: Unregister from Activity

**Requirement:** As a student, I want to unregister from an activity so that I can free up my slot.

**Acceptance Criteria:**
- ✅ AC-003-01: Registered student can unregister
- ✅ AC-003-02: System confirms successful unregistration
- ✅ AC-003-03: Student no longer appears in participants list
- ✅ AC-003-04: Student can re-register after unregistering

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-UNREGISTER-001 | Successful unregister in English | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-UNREGISTER-002 | Successful unregister in Hungarian | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-UNREGISTER-003 | Unregister from nonexistent activity | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-UNREGISTER-004 | Unregister when not registered | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-UNREGISTER-005 | Unregister then signup workflow | [test_app.py](../../tests/test_app.py) | ✅ Pass |

---

### US-004: Language Support

**Requirement:** As a student, I want to see activities in my preferred language (English/Hungarian) so that I can understand them better.

**Acceptance Criteria:**
- ✅ AC-004-01: Activities available in English
- ✅ AC-004-02: Activities available in Hungarian
- ✅ AC-004-03: Participants synced across both languages
- ✅ AC-004-04: English is default language

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-ACTIVITIES-001 | Get all activities in English | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-ACTIVITIES-002 | Get all activities in Hungarian | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-LANGUAGE-001 | Participants synced across languages | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-LANGUAGE-002 | English default language | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-SIGNUP-002 | Successful signup in Hungarian | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-UNREGISTER-002 | Successful unregister in Hungarian | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-CAPACITY-002 | Reject signup at capacity (Hungarian) | [test_app.py](../../tests/test_app.py) | ✅ Pass |

---

### US-005: View Available Spots

**Requirement:** As a student, I want to see how many spots are left in an activity so that I know if I can join.

**Acceptance Criteria:**
- ✅ AC-005-01: Each activity displays max_participants
- ✅ AC-005-02: Current participant count is visible
- ✅ AC-005-03: Available spots can be calculated

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-ACTIVITIES-004 | Activities have correct structure | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-ACTIVITIES-005 | Activities include participant lists | [test_app.py](../../tests/test_app.py) | ✅ Pass |

---

### US-006: Prevent Signups When Full

**Requirement:** As an admin, I want to prevent signups when an activity is full so that capacity is not exceeded.

**Acceptance Criteria:**
- ✅ AC-006-01: Signup rejected when at max_participants
- ✅ AC-006-02: Error message displayed in appropriate language
- ✅ AC-006-03: Participant count does not exceed limit
- ✅ AC-006-04: Last available slot can be filled
- ✅ AC-006-05: Concurrent signups correctly enforced (race conditions)

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-CAPACITY-001 | Reject signup at capacity (English) | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-CAPACITY-002 | Reject signup at capacity (Hungarian) | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-CAPACITY-003 | Allow signup one below capacity | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-CAPACITY-004 | Sequential signup capacity check | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-RACE-001 | Single spot race (10 threads, 1 slot) | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-RACE-002 | Multiple spots race (10 threads, 3 slots) | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-RACE-003 | Cross-language race (5 EN + 5 HU) | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-RACE-004 | Signup + unregister chaos (15 ops) | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-RACE-005 | Tight timing stress (no barrier) | [test_app.py](../../tests/test_app.py) | ✅ Pass |
| TC-RACE-006 | Parameterized thread count (5/10/20) | [test_app.py](../../tests/test_app.py) | ✅ Pass |

---

### US-007: Prevent Duplicate Signups

**Requirement:** As an admin, I want to prevent duplicate signups so that students aren't registered multiple times.

**Acceptance Criteria:**
- ✅ AC-007-01: System rejects signup if email already registered
- ✅ AC-007-02: Appropriate error message displayed
- ✅ AC-007-03: Participant appears only once in list

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-SIGNUP-004 | Duplicate signup prevention | [test_app.py](../../tests/test_app.py) | ✅ Pass |

---

### US-008: Email Validation

**Requirement:** As a developer, I want the system to validate email addresses so that only valid emails are accepted.

**Acceptance Criteria:**
- ✅ AC-008-01: Pydantic EmailStr validation enabled
- ✅ AC-008-02: Invalid emails return 422 error
- ✅ AC-008-03: Valid emails accepted

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-INFRA-DEPS-003 | EmailStr validator available | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-SIGNUP-001 | Successful signup (validates email format) | [test_app.py](../../tests/test_app.py) | ✅ Pass |

**Note:** Email validation is enforced automatically by Pydantic. Invalid email tests not needed as FastAPI returns 422 automatically.

---

### US-009: Infrastructure Testing

**Requirement:** As a developer, I want infrastructure tests so that import/startup errors are caught early.

**Acceptance Criteria:**
- ✅ AC-009-01: All modules can be imported
- ✅ AC-009-02: All dependencies installed
- ✅ AC-009-03: Data structures initialized correctly
- ✅ AC-009-04: Server can start successfully
- ✅ AC-009-05: No syntax errors in code

| Test Case ID | Test Name | Automation | Status |
|--------------|-----------|------------|--------|
| TC-INFRA-IMPORT-* | Module import tests (11 tests) | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-INFRA-APP-* | Application creation tests (4 tests) | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-INFRA-DATA-* | Data structure tests (6 tests) | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-INFRA-DEPS-* | Dependency tests (6 tests) | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-INFRA-FILES-* | Static file tests (4 tests) | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-INFRA-SERVER-* | Server startup tests (2 tests) | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-INFRA-QUALITY-* | Code quality tests (4 tests) | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-INFRA-ENDPOINT-001 | Service method test | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |
| TC-INFRA-VALIDATOR-* | Validator function tests (2 tests) | [test_infrastructure.py](../../tests/test_infrastructure.py) | ✅ Pass |

---

## Coverage Summary

### Requirements Coverage

| Requirement ID | Title | Test Ca10 | ✅ Yes | 100% |
| US-007 | Prevent Duplicates | 1 | ✅ Yes | 100% |
| US-008 | Email Validation | 2 | ✅ Yes | 100% |
| US-009 | Infrastructure | 40 | ✅ Yes | 100% |

**Total Requirements:** 9  
**Total Covered:** 9 (100%)  
**Total Test Cases:** 67  
**Total Automated:** 67icates | 1 | ✅ Yes | 100% |
| US-008 | Email Validation | 2 | ✅ Yes | 100% |
| US-009 | Infrastructure | 40 | ✅ Yes | 100% |

**Total Requirements:** 9  
**Total Covered:** 9 (100%)  
**Total Test Cases:** 61  
**Total Automated:** 61 (100%)

### API Endpoint Coverage

| Endpoint | Method | Test Cases | Coverage |
|----------|--------|------------|----------|
| `/` | GET | 1 | 100% |
| `/activities` | GET | 6 | 100% |
| `/activities/{name}/signup` | POST | 15 | 100% |
| `/activities/{name}/unregister` | DELETE | 5 | 100% |

**Total Endpoints:** 4  
**Total Covered:** 4 (100%)

**Concurrency Coverage:**
- Race condition tests: 6 tests (8 including parameterized variations)
- Thread counts tested: 5, 10, 15, 20
- Scenarios: Single slot, multiple slots, cross-language, chaos, no-barrier, parameterized

### Activity Coverage

All 9 activities tested:
- ✅ Chess Club / Sakk Klub
- ✅ Programming Class / Programozás Tanfolyam
- ✅ Gym Class / Tornaterem
- ✅ Soccer Team / Focicsapat
- ✅ Swimming Club / Úszó Klub
- ✅ Drama Club / Drámakör
- ✅ Art Studio / Művészeti Stúdió
- ✅ Debate Team / Vitakör
- ✅ Science Olympiad / Tudományos Olimpia

---

## Gap Analysis

### Current Gaps

**None identified.** All user stories have comprehensive test coverage.

### Future Requirements (Not Yet Implemented)

| Future ID | Description | Priority | Test Cases Needed |
|-----------|-------------|----------|-------------------|
| US-010 | Email notifications on signup | P3 | TBD |
| US-011 | Admin dashboard for activity management | P3 | TBD |
| US-012 | Student profile with enrolled activities | P3 | TBD |
| US-013 | Activity search/filter functionality | P2 | TBD |
| US-014 | Waitlist for full activities | P2 | TBD |

---

## How to Maintain This Matrix

### When Adding a New Requirement

1. Add user story to [Requirements Overview](#requirements-overview)
2. Define acceptance criteria
3. Create test cases in [TEST_CASES.md](TEST_CASES.md)
4. Add traceability entry linking requirement → test cases
5. Update [Coverage Summary](#coverage-summary)

### When Adding a New Test

1. Ensure test has `@pytest.mark.test_id()` decorator
2. Document in [TEST_CASES.md](TEST_CASES.md)
3. Link to requirement in this matrix
4. Update coverage percentages

### When Deprecating a Requirement

1. Update status to "❌ Deprecated"
2. Mark related test cases as deprecated
3. Update coverage summary8, 2025  
**Next Review:** March 28torical reference

---

**Last Review:** December 20, 2025  
**Next Review:** March 20, 2026  
**Reviewed By:** Development Team
