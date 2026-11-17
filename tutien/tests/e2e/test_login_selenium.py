"""Demo 8 - Selenium WebDriver: kiểm thử giao diện trên trình duyệt thật (Chrome headless).

Fixture `live_server` tự bật uvicorn trên cổng trống với DB tạm; không đụng dữ liệu thật.
Cần: Google Chrome đã cài (Selenium Manager tự tải chromedriver tương ứng).
Chạy:   pytest -m e2e -v        Bỏ qua:  pytest -m "not e2e"
Xem trình duyệt chạy:  HEADLESS=0 pytest -m e2e
"""
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen

import pytest

pytestmark = pytest.mark.e2e

selenium = pytest.importorskip("selenium")
from selenium import webdriver  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402

ROOT = Path(os.environ["TUTIEN_HOME"])
SHOTS = Path(__file__).resolve().parents[2] / "docs" / "screenshots"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def live_server():
    port = _free_port()
    data_dir = tempfile.mkdtemp(prefix="tutien_e2e_")
    env = {**os.environ, "TU_TIEN_DATA_DIR": data_dir, "TU_TIEN_DATABASE_PATH": "e2e.db"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(160):                       # chờ tối đa ~80s để app khởi động
            if proc.poll() is not None:
                pytest.fail("uvicorn thoát sớm khi khởi động")
            try:
                if urlopen(base + "/robots.txt", timeout=1).status == 200:
                    break
            except Exception:
                time.sleep(0.5)
        else:
            pytest.fail("Server không sẵn sàng")
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture
def driver():
    opts = webdriver.ChromeOptions()
    if os.environ.get("HEADLESS", "1") != "0":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--disable-gpu")
    try:
        drv = webdriver.Chrome(options=opts)
    except Exception as e:                         # không có Chrome/driver -> bỏ qua thay vì lỗi
        pytest.skip(f"Không khởi động được Chrome: {e}")
    drv.implicitly_wait(2)
    yield drv
    drv.quit()


def _shot(drv, name):
    SHOTS.mkdir(parents=True, exist_ok=True)
    drv.save_screenshot(str(SHOTS / f"{name}.png"))


def _wait(drv, locator, timeout=15):
    return WebDriverWait(drv, timeout).until(EC.visibility_of_element_located(locator))


def test_trang_chu_hien_form_dang_nhap(live_server, driver):
    driver.get(live_server + "/")
    assert _wait(driver, (By.ID, "username")).is_displayed()
    assert driver.find_element(By.ID, "password").get_attribute("type") == "password"
    _shot(driver, "01_trang_dang_nhap")


def test_chuyen_tab_tao_tai_khoan(live_server, driver):
    driver.get(live_server + "/")
    _wait(driver, (By.ID, "authTabRegister")).click()
    assert _wait(driver, (By.ID, "regUsername")).is_displayed()
    assert not driver.find_element(By.ID, "authLoginView").is_displayed()
    _shot(driver, "02_tab_tao_tai_khoan")


def test_dang_nhap_sai_hien_thong_bao_loi(live_server, driver):
    driver.get(live_server + "/")
    _wait(driver, (By.ID, "username")).send_keys("khongtontai")
    driver.find_element(By.ID, "password").send_keys("sai-mat-khau")
    driver.find_element(By.CSS_SELECTOR, "#authLoginView button[type=submit], #authLoginView button").click()
    # Ban đầu #authMsg hiện "Đang đăng nhập..." -> chờ tới khi server trả lỗi thật (explicit wait)
    WebDriverWait(driver, 20).until(
        EC.text_to_be_present_in_element((By.ID, "authMsg"), "Sai tài khoản hoặc mật khẩu")
    )
    assert "Sai tài khoản hoặc mật khẩu" in driver.find_element(By.ID, "authMsg").text
    _shot(driver, "03_dang_nhap_sai")


def test_dang_ky_roi_vao_man_tao_nhan_vat(live_server, driver):
    driver.get(live_server + "/")
    _wait(driver, (By.ID, "authTabRegister")).click()
    _wait(driver, (By.ID, "regUsername")).send_keys("selenium_user")
    driver.find_element(By.ID, "regPassword").send_keys("matkhau123")
    driver.find_element(By.ID, "regPassword2").send_keys("matkhau123")
    driver.find_element(By.CSS_SELECTOR, "#authRegisterView button[type=submit], #authRegisterView button").click()
    panel = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "characterSetupPanel"))
    )
    assert panel.is_displayed()
    _shot(driver, "04_tao_nhan_vat")
