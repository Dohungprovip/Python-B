from pathlib import Path

import pytest

pytest.importorskip("selenium")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.selenium

PAGE_URL = (Path(__file__).resolve().parent.parent / "web" / "todo.html").as_uri()


def _make_driver():
    errors = []
    for name, options_cls, driver_cls in (
        ("chrome", webdriver.ChromeOptions, webdriver.Chrome),
        ("edge", webdriver.EdgeOptions, webdriver.Edge),
    ):
        try:
            options = options_cls()
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1000,800")
            return driver_cls(options=options)
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}")
    pytest.skip("Không khởi tạo được trình duyệt: " + "; ".join(errors))


@pytest.fixture(scope="module")
def browser():
    driver = _make_driver()
    yield driver
    driver.quit()


@pytest.fixture
def page(browser):
    browser.get(PAGE_URL)
    return browser


def add_task(driver, text):
    driver.find_element(By.ID, "task").send_keys(text)
    driver.find_element(By.ID, "add").click()


def test_page_title(page):
    assert page.title == "Todo Demo"
    assert page.find_element(By.TAG_NAME, "h1").text == "Danh sách việc cần làm"


def test_add_task(page):
    add_task(page, "Học Selenium")
    items = page.find_elements(By.CSS_SELECTOR, "#list li")
    assert len(items) == 1
    assert "Học Selenium" in items[0].text
    assert page.find_element(By.ID, "count").text == "1"
    assert page.find_element(By.ID, "task").get_attribute("value") == ""


def test_empty_task_shows_error(page):
    page.find_element(By.ID, "add").click()
    error = WebDriverWait(page, 5).until(
        EC.text_to_be_present_in_element((By.ID, "error"), "Không được để trống")
    )
    assert error
    assert page.find_elements(By.CSS_SELECTOR, "#list li") == []


def test_delete_task(page):
    add_task(page, "A")
    add_task(page, "B")
    assert page.find_element(By.ID, "count").text == "2"
    page.find_element(By.CSS_SELECTOR, "#list li .delete").click()
    assert page.find_element(By.ID, "count").text == "1"
