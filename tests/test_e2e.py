import re
'''
from flask import Flask
from database import init_database, add_sample_data
from routes import register_blueprints
'''
from app import create_app
from playwright.sync_api import Page, expect
from database import get_book_id_by_isbn, clear_all_data
'''
NOTE: It is expected that each test case below is to be ran sequentially. If this is not done, the test cases below could fail.
'''

    
def test_has_title(page: Page):
    """Sanity check to ensure website connection is working, additionally will set database to default before each other test."""
    clear_all_data()
    page.goto("http://localhost:5000")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Library Management System"))

def test_user_add_book(page: Page):
    """Test case that walks through the process of adding a new book."""
    page.goto("http://localhost:5000")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Library Management System"))
    expect(page).to_have_url("http://localhost:5000/catalog")

    # Go to the Add Book page and ensure we're on the right page
    page.get_by_role("link", name="➕ Add Book").click()
    expect(page).to_have_url("http://localhost:5000/add_book")
    expect(page.locator("h2")).to_contain_text("➕ Add New Book")

    # First, setup references to each input field
    title_box = page.get_by_role("textbox", name="Title *")
    author_box = page.get_by_role("textbox", name="Author *")
    isbn_box = page.get_by_role("textbox", name="ISBN *")
    copies_box = page.get_by_role("spinbutton", name="Total Copies *")

    # Enter all values by clicking each box, then entering in information
    title_box.click()
    title_box.fill("UI Testing: Tips and Tricks")
    author_box.click()
    author_box.fill("AJ. Smith")
    isbn_box.click()
    isbn_box.fill("4526138443166")
    copies_box.click()
    copies_box.fill("7")

    # Assert the values are what they should be
    expect(title_box).to_have_value("UI Testing: Tips and Tricks")
    expect(author_box).to_have_value("AJ. Smith")
    expect(isbn_box).to_have_value("4526138443166")
    expect(copies_box).to_have_value("7")

    # Add the book. This should return the user to the catalog page
    page.get_by_role("button", name="Add Book to Catalog").click()
    expect(page).to_have_url("http://localhost:5000/catalog")

    # Ensure success message appears and book is in catalog
    expect(page.locator("body")).to_contain_text("Book \"UI Testing: Tips and Tricks\" has been successfully added to the catalog.")
    expect(page.locator("tbody")).to_contain_text("UI Testing: Tips and Tricks")
    expect(page.locator("tbody")).to_contain_text("AJ. Smith")
    expect(page.locator("tbody")).to_contain_text("4526138443166")
    expect(page.locator("tbody")).to_contain_text("7/7 Available")

def test_user_borrow_book(page: Page):
    """Test case that walks through the process of borrowing a book."""
    page.goto("http://localhost:5000")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Library Management System"))
    expect(page).to_have_url("http://localhost:5000/catalog")

    # Ensure the book added from the last test exists
    expect(page.locator("tbody")).to_contain_text("UI Testing: Tips and Tricks")
    expect(page.locator("tbody")).to_contain_text("4526138443166")
    expect(page.locator("tbody")).to_contain_text("7/7 Available")
    
    # Get book id, since it's automatically set
    book_id = get_book_id_by_isbn("4526138443166")

    # The row name is the books info, limited to 25 characters.
    row_name = f"{book_id} UI Testing: Tips and Tricks"
    # Row names are limited by 25 characters. So truncate it.
    book_row = page.get_by_role("row", name=row_name[:25])

    # Fill in the patron ID info, ensure its been filled in, then borrow the book
    book_row.get_by_placeholder("Patron ID (6 digits)").click()
    book_row.get_by_placeholder("Patron ID (6 digits)").fill("678942")
    expect(page.get_by_role("cell", name="678942 Borrow").get_by_placeholder("Patron ID (6 digits)")).to_have_value("678942")
    page.get_by_role("cell", name="678942 Borrow").get_by_role("button").click()

    # Ensure that a borrow message appears and that the availability has been updated
    expect(page.get_by_text("Successfully borrowed \"UI")).to_be_visible()
    expect(page.locator("tbody")).to_contain_text("6/7 Available")

def test_user_return_book(page: Page):
    """Test case that walks through the process of returning a book."""
    page.goto("http://localhost:5000")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Library Management System"))
    expect(page).to_have_url("http://localhost:5000/catalog")

    # Go the the return book page, ensure we're at the page
    page.get_by_role("link", name="↩️ Return Book").click()
    expect(page).to_have_url("http://localhost:5000/return")
    expect(page.locator("h2")).to_contain_text("↩️ Return Book")

    # Setup references for the input fields
    patron_box = page.get_by_role("textbox", name="Patron ID *")
    id_box = page.get_by_role("spinbutton", name="Book ID *")
    # Get book id, since it's automatically set by database
    book_id = get_book_id_by_isbn("4526138443166")
    
    # Fill in the input fields with information
    patron_box.click()
    patron_box.fill("678942")
    id_box.click()
    id_box.fill(f"{book_id}")
    
    # Ensure each box has the information
    expect(patron_box).to_have_value("678942")
    expect(id_box).to_have_value(f"{book_id}")

    # Click the return button, ensure the return message appears
    page.get_by_role("button", name="Process Return").click()
    expect(page.get_by_text("Successfully returned \"UI")).to_be_visible()

    # Go back to the catalog page, ensure we're on the right page
    page.get_by_role("link", name="📖 Catalog").click()
    expect(page).to_have_url("http://localhost:5000/catalog")
    expect(page.locator("h2")).to_contain_text("📖 Book Catalog")

    # Ensure the returned book exists and has an updated copy count
    expect(page.locator("tbody")).to_contain_text("UI Testing: Tips and Tricks")
    expect(page.locator("tbody")).to_contain_text("7/7 Available")


def test_user_search_book(page: Page):
    """Test case that walks through the process of searching a book."""
    page.goto("http://localhost:5000")

    # Go to the search page, ensure we're on the right page
    page.get_by_role("link", name="🔍 Search").click()
    page.goto("http://localhost:5000/search")
    expect(page.locator("h2")).to_contain_text("🔍 Search Books")

    # Setup some variables for input fields
    search_type_box = page.get_by_label("Search Type")
    search_field = page.get_by_role("textbox", name="Search Term")

    # Fill in the search field with a search prompt
    search_field.click()
    search_field.fill("ui testing")

    # Ensure the search box has the right value, and that we're searching for titles
    expect(search_field).to_have_value("ui testing")
    expect(search_type_box).to_have_value("title")

    # Search and see if the UI Testing book appears in the results
    page.get_by_role("button", name="🔍 Search").click()
    expect(page.locator("h3")).to_contain_text("Search Results for \"ui testing\" (title)")
    expect(page.locator("tbody")).to_contain_text("UI Testing: Tips and Tricks")

    # Do the same, but for author searching
    search_type_box.select_option("author")
    search_field.click()
    search_field.fill("a")

    # Ensure the search box has the right value, and that we're searching for authors
    expect(search_field).to_have_value("a")
    expect(search_type_box).to_have_value("author")

    # Search and see if the AJ author appears in the results
    page.get_by_role("button", name="🔍 Search").click()
    expect(page.locator("h3")).to_contain_text("Search Results for \"a\" (author)")
    expect(page.locator("tbody")).to_contain_text("AJ. Smith")

    # Do the same again, but with ISBN
    search_type_box.select_option("isbn")
    search_field.click()
    search_field.fill("4526138443166")

    # Ensure the search box has the right value, and that we're searching for ISBN
    expect(search_field).to_have_value("4526138443166")
    expect(search_type_box).to_have_value("isbn")

    # Search and see if the right ISBN appears in the results
    page.get_by_role("button", name="🔍 Search").click()
    expect(page.locator("h3")).to_contain_text("Search Results for \"4526138443166\" (isbn)")
    expect(page.locator("tbody")).to_contain_text("4526138443166")

    # Clean all test data after the last test
    clear_all_data()
