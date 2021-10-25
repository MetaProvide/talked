import time
import subprocess
import logging
import sys
import pkgutil
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from pyvirtualdisplay import Display
from threading import Event
from queue import Queue
from talked import config
from talked.ffmpeg import assemble_command

msg_queue = None


def start(token: str, queue: Queue, recording: Event, audio_only: bool) -> None:
    global msg_queue
    msg_queue = queue

    # Assemble link for call to record
    call_link = assemble_call_link(config["base_url"], token)

    # Make sure an instance of Pulseaudio is running.
    logging.info("Starting pulseaudio")
    subprocess.run(["pulseaudio", "--start"])

    logging.info("Starting virtual x server")
    with Display(
        backend="xvfb",
        size=(config["video_width"], config["video_height"]),
        color_depth=config["color_depth"],
    ):
        logging.info("Starting browser")
        logging.info(call_link)
        browser = launch_browser(call_link)
        logging.info("Starting ffmpeg process")

        try:
            ffmpeg_command = assemble_command(audio_only)
        except RuntimeError:
            msg_queue.put(
                {
                    "status": "error",
                    "message": (
                        "There was an issue with the recording configuration, "
                        "please contact an administrator."
                    ),
                }
            )
            graceful_shutdown(browser)

        ffmpeg = subprocess.Popen(ffmpeg_command)
        logging.info("Recording has started")

        msg_queue.put(
            {
                "status": "ok",
                "message": "Recording has started.",
            }
        )

        recording.wait()

        logging.info("Stop ffmpeg process")
        ffmpeg.terminate()
        logging.info("Stop browser")
        browser.close()
        msg_queue.put(
            {
                "status": "ok",
                "message": "Recording has stopped.",
            }
        )


def launch_browser(call_link: str) -> WebDriver:
    logging.info("Configuring browser options")
    options = Options()
    options.set_preference("media.navigator.permission.disabled", True)
    options.set_preference("privacy.webrtc.legacyGlobalIndicator", False)
    options.set_preference("full-screen-api.warning.timeout", 0)
    options.add_argument("--kiosk")
    options.add_argument(f"--width={config['video_width']}")
    options.add_argument(f"--height={config['video_height']}")

    logging.info("Creating browser")
    driver = Firefox(options=options)
    logging.info("Navigate to call link")
    driver.get(call_link)

    # Check if loaded page is a valid Talk room
    is_valid_talk_room(driver)

    # Change the name of the recording user
    logging.info("Changing name of recording user")
    change_name_of_user(driver)

    join_call(driver)

    # Get page body to send keyboard shortcuts
    page = driver.find_element_by_tag_name("body")

    # Press escape to remove focus from chat.
    page.send_keys(Keys.ESCAPE)
    # Press m to mute the microphone, if there is one attached.
    page.send_keys("m")

    # If grid view is set to False, switch to speaker view.
    if not config["grid_view"]:
        switch_to_speaker_view(driver)

    close_sidebar(driver)

    # Go fullscreen
    page.send_keys("f")

    logging.info("Loading custom CSS")
    load_custom_css(driver)

    # Give it some time to properly connect to participants.
    time.sleep(5)
    return driver


def assemble_call_link(base_url: str, token: str) -> str:
    return base_url + "/index.php/call/" + token


def is_valid_talk_room(driver: WebDriver) -> None:
    """Checks if the loaded page is a valid Talk room.
    It looks for the start call / join call button, if it isn't there
    it throws a TimeoutException notifies the HTTP api
    and shuts down the browser.

    Accepts the current browser driver.
    """

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".app-talk .top-bar .top-bar__button")
            )
        )
    except TimeoutException:
        msg_queue.put(
            {
                "status": "error",
                "message": "Failed to load the Talk room.",
            }
        )
        logging.warning("Failed to load the Talk room.")
        graceful_shutdown(driver)


def change_name_of_user(driver: WebDriver) -> None:
    edit_name = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".username-form button.icon-rename")
        )
    )
    edit_name.click()
    driver.find_element_by_css_selector("input.username-form__input").send_keys(
        "Talked" + Keys.ENTER
    )


def join_call(driver: WebDriver) -> None:
    # Wait for the green Join Call button to appear then click it
    logging.info("Waiting for join call button to appear")
    try:
        join_call = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "button.top-bar__button.success")
            )
        )
    except TimeoutException:
        msg_queue.put(
            {
                "status": "error",
                "message": "There doesn't seem to be an active call in the room.",
            }
        )
        logging.warning("There doesn't seem to be an active call in the room.")
        graceful_shutdown(driver)

    time.sleep(2)
    logging.info("Joining call")
    join_call.click()

    # Wait for the call to initiate
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".top-bar.in-call"))
        )
    except TimeoutException:
        msg_queue.put(
            {
                "status": "error",
                "message": "Failed to initiate call.",
            }
        )
        logging.warning("Failed to initiate call.")
        graceful_shutdown(driver)


def switch_to_speaker_view(driver: WebDriver) -> None:
    # Switch to speaker view
    logging.info("Switching to speaker view")
    try:
        driver.find_element_by_css_selector(
            ".top-bar.in-call button.icon-promoted-view"
        ).click()
    except NoSuchElementException:
        logging.info(
            (
                "Speaker view button wasn't found. "
                "Assuming we are already in speaker view."
            )
        )


def close_sidebar(driver: WebDriver) -> None:
    # Close the sidebar
    logging.info("Closing sidebar")
    try:
        driver.find_element_by_css_selector("a.app-sidebar__close").click()
    except ElementClickInterceptedException:
        logging.info("Assuming toast is covering close button")
        close_toasts(driver)
        driver.find_element_by_css_selector("a.app-sidebar__close").click()

    # Wait for sidebar to close
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".top-bar.in-call button.top-bar__button .icon-leave-call",
            )
        )
    )


def close_toasts(driver: WebDriver) -> None:
    while True:
        logging.info("Closing toast")
        try:
            driver.find_element_by_css_selector("span.toast-close").click()
        except NoSuchElementException:
            logging.info("No more open toasts")
            break


def load_custom_css(driver: WebDriver) -> None:
    javascript = pkgutil.get_data("talked", "static/custom_css.js").decode("UTF-8")
    driver.execute_script(javascript)


def graceful_shutdown(driver: WebDriver) -> None:
    logging.info("Shutting down...")
    driver.close()
    sys.exit()
