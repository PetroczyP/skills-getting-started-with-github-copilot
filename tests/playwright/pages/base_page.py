"""Base Page Object Model for common functionality.

This module provides the base class for all Page Objects with common
navigation, waiting, and utility methods.
"""

from playwright.sync_api import Page, expect
from typing import Optional


class BasePage:
    """Base Page Object with common functionality."""
    
    def __init__(self, page: Page, base_url: str = "http://localhost:8000"):
        """Initialize the base page.
        
        Args:
            page: Playwright Page object
            base_url: Base URL for the application
        """
        self.page = page
        self.base_url = base_url
    
    def navigate_to(self, path: str = "/") -> None:
        """Navigate to a specific path.
        
        Args:
            path: Path relative to base URL
        """
        url = f"{self.base_url}{path}"
        self.page.goto(url)
    
    def wait_for_url(self, url_pattern: str, timeout: int = 30000) -> None:
        """Wait for URL to match pattern.
        
        Args:
            url_pattern: URL pattern to wait for
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_url(url_pattern, timeout=timeout)
    
    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 30000) -> None:
        """Wait for selector to be in specific state.
        
        Args:
            selector: CSS selector
            state: State to wait for (visible, hidden, attached, detached)
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_selector(selector, state=state, timeout=timeout)
    
    def wait_for_timeout(self, timeout: int) -> None:
        """Wait for a specific amount of time.
        
        Args:
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_timeout(timeout)
    
    def get_text(self, selector: str) -> str:
        """Get text content of an element.
        
        Args:
            selector: CSS selector
            
        Returns:
            Text content of the element
        """
        return self.page.locator(selector).text_content() or ""
    
    def click(self, selector: str) -> None:
        """Click an element.
        
        Args:
            selector: CSS selector
        """
        self.page.locator(selector).click()
    
    def fill(self, selector: str, value: str) -> None:
        """Fill an input field.
        
        Args:
            selector: CSS selector
            value: Value to fill
        """
        self.page.locator(selector).fill(value)
    
    def select_option(self, selector: str, value: str) -> None:
        """Select an option from a dropdown.
        
        Args:
            selector: CSS selector
            value: Option value to select
        """
        self.page.locator(selector).select_option(value)
    
    def is_visible(self, selector: str) -> bool:
        """Check if an element is visible.
        
        Args:
            selector: CSS selector
            
        Returns:
            True if element is visible, False otherwise
        """
        return self.page.locator(selector).is_visible()
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute value of an element.
        
        Args:
            selector: CSS selector
            attribute: Attribute name
            
        Returns:
            Attribute value or None
        """
        return self.page.locator(selector).get_attribute(attribute)
    
    def reload(self) -> None:
        """Reload the current page."""
        self.page.reload()
    
    def screenshot(self, path: str) -> None:
        """Take a screenshot of the current page.
        
        Args:
            path: Path to save screenshot
        """
        self.page.screenshot(path=path)
