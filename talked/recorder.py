import time
import subprocess
import logging
import sys

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import TimeoutException

from pyvirtualdisplay import Display


def start(config):
    # Make sure an instance of Pulseaudio is running.
    logging.debug("Starting pulseaudio")
    subprocess.run(["pulseaudio", "--start"])

    logging.debug("Starting virtual x server")
    with Display(backend="xvfb", size=(1920, 1080), color_depth=24) as display:
        logging.debug("Starting browser")
        browser = launch_browser(config["call_link"])
        logging.debug("Starting ffmpeg process")
        ffmpeg = subprocess.Popen(
            [
                "ffmpeg",
                "-nostdin",
                "-nostats",
                "-hide_banner",
                "-loglevel",
                "warning",
                "-fflags",
                "+igndts",
                "-f",
                "x11grab",
                "-video_size",
                "1920x1080",
                "-framerate",
                "30",
                "-draw_mouse",
                "0",
                "-thread_queue_size",
                "4096",
                "-i",
                display.env()["DISPLAY"],
                "-f",
                "pulse",
                "-ac",
                "2",
                "-channel_layout",
                "stereo",
                "-thread_queue_size",
                "4096",
                "-i",
                "0",
                "-c:v",
                "libx264",
                "-crf",
                "25",
                "-preset",
                "veryfast",
                "-threads",
                "1",
                f"{time.strftime('%Y%m%dT%H%M%S')}_output.mp4",
            ]
        )
        logging.info("Recording has started")
        time.sleep(30)
        logging.debug("Stop ffmpeg process")
        ffmpeg.terminate()
        logging.debug("Stop browser")
        browser.close()


def launch_browser(call_link):
    logging.debug("Configuring browser options")
    options = Options()
    options.set_preference("media.navigator.permission.disabled", True)
    options.set_preference("privacy.webrtc.legacyGlobalIndicator", False)
    options.set_preference("full-screen-api.warning.timeout", 0)
    options.add_argument("--kiosk")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    logging.debug("Creating browser")
    driver = Firefox(options=options)
    logging.debug("Navigate to call link")
    driver.get(call_link)

    # Change the name of the recording user
    logging.debug("Changing name of recording user")
    change_name_of_user(driver)

    join_call(driver)

    # Get page body to send keyboard shortcuts
    page = driver.find_element_by_tag_name("body")

    # Press escape to remove focus from chat.
    page.send_keys(Keys.ESCAPE)
    # Press m to mute the microphone, if there is one attached.
    page.send_keys("m")

    switch_to_speaker_view(driver)

    close_sidebar(driver)

    # Go fullscreen
    page.send_keys("f")

    logging.debug("Loading custom CSS")
    load_custom_css(driver)

    # Give it some time to properly connect to participants.
    time.sleep(5)
    return driver


def change_name_of_user(driver):
    edit_name = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".username-form button.icon-rename")
        )
    )
    edit_name.click()
    driver.find_element_by_css_selector("input.username-form__input").send_keys(
        "Talked" + Keys.ENTER
    )


def join_call(driver):
    # Wait for the green Join Call button to appear then click it
    logging.debug("Waiting for join call button to appear")
    try:
        join_call = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "button.top-bar__button.success")
            )
        )
    except TimeoutException:
        graceful_shutdown(
            driver, "There doesn't seem to be an active called in the requested room."
        )

    time.sleep(2)
    logging.debug("Joining call")
    join_call.click()

    # Wait for the call to initiate
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".top-bar.in-call"))
        )
    except TimeoutException:
        graceful_shutdown(driver, "Failed to initiate call.")


def switch_to_speaker_view(driver):
    # Switch to speaker view
    logging.debug("Switching to speaker view")
    speaker_view = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".top-bar.in-call button.icon-promoted-view")
        )
    )
    speaker_view.click()


def close_sidebar(driver):
    # Close the sidebar
    logging.debug("Closing sidebar")
    sidebar_close = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "a.app-sidebar__close"))
    )
    sidebar_close.click()

    # Wait for sidebar to close
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".top-bar.in-call button.top-bar__button.icon-menu-people",
            )
        )
    )


def load_custom_css(driver):
    with open("custom_css.js") as f:
        javascript = "".join(line.strip() for line in f)
    driver.execute_script(javascript)


def graceful_shutdown(driver, error_msg):
    driver.close()
    sys.exit(error_msg)
