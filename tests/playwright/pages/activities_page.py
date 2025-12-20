"""Page Object Model for the Activities page.

This module provides the ActivitiesPage class with methods for interacting
with the main activities page including language switching, signup, and
participant management.
"""

from playwright.sync_api import Page, expect, Dialog
from typing import List, Optional
from .base_page import BasePage


class ActivitiesPage(BasePage):
    """Page Object for the Activities page."""
    
    def __init__(self, page: Page, base_url: str = "http://localhost:8000"):
        """Initialize the Activities page.
        
        Args:
            page: Playwright Page object
            base_url: Base URL for the application
        """
        super().__init__(page, base_url)
        
        # Locators for language switcher
        self.language_en_btn = page.locator('button[data-lang="en"]')
        self.language_hu_btn = page.locator('button[data-lang="hu"]')
        
        # Locators for signup form
        self.email_input = page.locator('#email')
        self.activity_select = page.locator('#activity')
        self.signup_button = page.locator('#signup-form button[type="submit"]')
        
        # Locators for messages and content
        self.message_div = page.locator('#message')
        self.activities_list = page.locator('#activities-list')
        self.page_title = page.locator('h2[data-i18n="page-title"]')
        self.signup_title = page.locator('h3[data-i18n="signup-title"]')
    
    def load(self, clear_storage: bool = True) -> None:
        """Navigate to the activities page and wait for it to load.
        
        Args:
            clear_storage: Whether to clear localStorage before loading (default: True)
        """
        if clear_storage:
            # Navigate first to establish page context
            self.navigate_to("/")
            # Clear localStorage to ensure clean state
            self.page.evaluate("() => localStorage.clear()")
            # Reload to apply cleared storage
            self.page.reload()
        else:
            self.navigate_to("/")
        
        self.wait_for_activities_loaded()
    
    def wait_for_activities_loaded(self, timeout: int = 30000) -> None:
        """Wait for activities list to be loaded.
        
        Args:
            timeout: Timeout in milliseconds
        """
        self.wait_for_selector("#activities-list", state="visible", timeout=timeout)
        # Wait for at least one activity card to appear
        self.page.wait_for_selector(".activity-card", state="visible", timeout=timeout)
    
    def switch_to_language(self, lang: str) -> None:
        """Switch to specified language.
        
        Args:
            lang: Language code ('en', 'english', 'hu', 'hungarian')
        """
        lang_lower = lang.lower()
        if lang_lower in ["hungarian", "hu"]:
            self.language_hu_btn.click()
        else:
            self.language_en_btn.click()
        
        # Wait for translation to complete
        self.wait_for_timeout(200)
    
    def get_current_language(self) -> str:
        """Get the currently selected language.
        
        Returns:
            Language code ('en' or 'hu')
        """
        return self.page.evaluate("() => localStorage.getItem('lang')") or "en"
    
    def signup(self, email: str, activity: str) -> None:
        """Fill and submit the signup form.
        
        Args:
            email: Student email address
            activity: Activity name
        """
        self.email_input.fill(email)
        self.activity_select.select_option(activity)
        self.signup_button.click()
        
        # Wait for message to appear
        self.wait_for_timeout(500)
    
    def get_success_message(self) -> str:
        """Get text of success/error message.
        
        Returns:
            Message text
        """
        return self.message_div.text_content() or ""
    
    def is_message_visible(self) -> bool:
        """Check if message div is visible (not hidden).
        
        Returns:
            True if message is visible
        """
        message_classes = self.message_div.get_attribute("class") or ""
        return "hidden" not in message_classes
    
    def is_success_message(self, timeout: int = 5000) -> bool:
        """Check if displayed message is a success message.
        
        Args:
            timeout: Timeout in milliseconds to wait for message
            
        Returns:
            True if message has success class
        """
        try:
            # Wait for message to appear and have success class
            self.message_div.wait_for(state="visible", timeout=timeout)
            message_classes = self.message_div.get_attribute("class") or ""
            return "success" in message_classes
        except Exception:
            return False
    
    def is_error_message(self, timeout: int = 5000) -> bool:
        """Check if displayed message is an error message.
        
        Args:
            timeout: Timeout in milliseconds to wait for message
            
        Returns:
            True if message has error class
        """
        try:
            # Wait for message to appear and have error class
            self.message_div.wait_for(state="visible", timeout=timeout)
            message_classes = self.message_div.get_attribute("class") or ""
            return "error" in message_classes
        except Exception:
            return False
    
    def get_activity_card(self, activity_name: str):
        """Get the activity card element for a specific activity.
        
        Args:
            activity_name: Name of the activity
            
        Returns:
            Locator for the activity card
        """
        return self.page.locator(f'.activity-card:has-text("{activity_name}")')
    
    def get_participant_count(self, activity_name: str) -> int:
        """Get number of participants for an activity.
        
        Args:
            activity_name: Name of the activity
            
        Returns:
            Number of participants
        """
        card = self.get_activity_card(activity_name)
        participants = card.locator('.participants-list li')
        return participants.count()
    
    def get_participants(self, activity_name: str) -> List[str]:
        """Get list of participant emails for an activity.
        
        Args:
            activity_name: Name of the activity
            
        Returns:
            List of participant email addresses
        """
        card = self.get_activity_card(activity_name)
        participants = card.locator('.participants-list li')
        count = participants.count()
        
        emails = []
        for i in range(count):
            email_text = participants.nth(i).locator('span').text_content() or ""
            emails.append(email_text)
        
        return emails
    
    def has_participant(self, activity_name: str, email: str, timeout: int = 5000) -> bool:
        """Check if a participant is in an activity.
        
        Args:
            activity_name: Name of the activity
            email: Participant email
            timeout: Timeout in milliseconds to wait for participant list to update
            
        Returns:
            True if participant is in the list
        """
        # Wait a moment for UI to update after operations
        self.page.wait_for_timeout(1000)
        
        # Retry a few times to handle async updates
        for attempt in range(3):
            participants = self.get_participants(activity_name)
            if email in participants:
                return True
            if attempt < 2:  # Don't wait after last attempt
                self.page.wait_for_timeout(1000)
        
        return False
    
    def delete_participant(self, email: str, activity: str, confirm: bool = True) -> None:
        """Click delete button for a participant.
        
        Args:
            email: Participant email
            activity: Activity name
            confirm: Whether to confirm the dialog (True) or dismiss (False)
        """
        # Setup dialog handler before clicking
        def handle_dialog(dialog: Dialog):
            if confirm:
                dialog.accept()
            else:
                dialog.dismiss()
        
        self.page.once("dialog", handle_dialog)
        
        # Click delete button
        delete_btn = self.page.locator(
            f'.delete-btn[data-email="{email}"][data-activity="{activity}"]'
        )
        delete_btn.click()
        
        # Wait for action to complete
        self.wait_for_timeout(500)
    
    def get_activity_dropdown_options(self) -> List[str]:
        """Get list of activities available in the dropdown.
        
        Returns:
            List of activity names
        """
        options = self.activity_select.locator('option').all_text_contents()
        # Filter out the placeholder option
        return [opt for opt in options if opt and not opt.startswith("--")]
    
    def get_spots_left(self, activity_name: str) -> Optional[int]:
        """Get number of spots left for an activity.
        
        Args:
            activity_name: Name of the activity
            
        Returns:
            Number of spots left or None if not found
        """
        card = self.get_activity_card(activity_name)
        availability_text = card.locator('p:has-text("Availability:")').text_content() or ""
        
        # Extract number from text like "5 spots left"
        import re
        match = re.search(r'(\d+)\s+', availability_text)
        if match:
            return int(match.group(1))
        return None
    
    def verify_translation(self, selector: str, expected_text: str) -> None:
        """Verify element has expected translated text.
        
        Args:
            selector: CSS selector
            expected_text: Expected text content
        """
        expect(self.page.locator(selector)).to_have_text(expected_text)
    
    def get_page_title_text(self) -> str:
        """Get the page title text.
        
        Returns:
            Page title text
        """
        return self.page_title.text_content() or ""
    
    def get_signup_title_text(self) -> str:
        """Get the signup section title text.
        
        Returns:
            Signup title text
        """
        return self.signup_title.text_content() or ""
    
    def is_form_reset(self) -> bool:
        """Check if the signup form has been reset.
        
        Returns:
            True if form is empty
        """
        email_value = self.email_input.input_value()
        activity_value = self.activity_select.input_value()
        return email_value == "" and activity_value == ""
