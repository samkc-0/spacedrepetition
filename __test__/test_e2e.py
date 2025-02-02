import pytest
from playwright.sync_api import Page, expect
from dotenv import dotenv_values
import re


config = dotenv_values(".env")

page_url = f"http://localhost:{config["PORT"]}"


def test_has_title(page: Page):
    page.goto(page_url)

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("[Ll]ogin"))


def test_get_started_link(page: Page):
    page.goto(page_url)

    # Click the get started link.
    page.get_by_role("link", name="register").click()

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="User Registration")).to_be_visible()
