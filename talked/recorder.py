import logging
import pkgutil
import subprocess
import sys
import time
from queue import Queue
from threading import Event

from pyvirtualdisplay import Display
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from talked import config
from talked.ffmpeg import assemble_command


def start(
    token: str,
    queue: Queue,
    recording: Event,
    nextcloud_version: str,
    audio_only: bool,
    grid_view: bool,
) -> None:
    msg_queue = queue

    # Assemble link for call to record
    call_link = assemble_call_link(config["base_url"], token)  # type: ignore

    # Make sure an instance of Pulseaudio is running.
    logging.info("Starting pulseaudio")
    subprocess.run(["pulseaudio", "--start"], check=True)  # nosec

    logging.info("Starting virtual x server")
    with Display(
        backend="xvfb",
        size=(config["video_width"], config["video_height"]),
        color_depth=config["color_depth"],
    ):
        logging.info("Starting browser")
        logging.info(call_link)
        browser = launch_browser(call_link, msg_queue, nextcloud_version, grid_view)
        logging.info("Starting ffmpeg process")

        try:
            ffmpeg_command, filename = assemble_command(audio_only)
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

        ffmpeg = subprocess.Popen(ffmpeg_command)  # nosec
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
        logging.info("Recording has stopped")
        msg_queue.put(
            {
                "status": "ok",
                "message": "Recording has stopped.",
            }
        )

        if config.get("finalise_recording_script", ""):
            logging.info("Running finalise recording script")
            try:
                subprocess.run(  # nosec
                    [
                        config["finalise_recording_script"],
                        f"{config['recording_dir']}/{filename}",
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError:
                logging.error(
                    "The finalise recording script failed to run successfully!"
                )

        logging.info("Done!")


def launch_browser(
    call_link: str, msg_queue: Queue, nextcloud_version: str, grid_view: bool
) -> WebDriver:
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
    is_valid_talk_room(driver, msg_queue)

    # Change the name of the recording user
    change_name_of_user(driver)

    join_call(driver, msg_queue, nextcloud_version)

    # Get page body to send keyboard shortcuts
    page = driver.find_element_by_tag_name("body")

    # Press escape to remove focus from chat.
    page.send_keys(Keys.ESCAPE)
    # Mute the talked user
    mute_user(driver)

    # If grid view is set to False, switch to speaker view.
    if not grid_view:
        switch_to_speaker_view(driver, nextcloud_version)

    close_sidebar(driver)

    # Go fullscreen
    page.send_keys("f")

    # Load custom CSS used to improve the recording
    load_custom_css(driver)

    # Give it some time to properly connect to participants.
    time.sleep(5)
    return driver


def assemble_call_link(base_url: str, token: str) -> str:
    return base_url + "/index.php/call/" + token


def is_valid_talk_room(driver: WebDriver, msg_queue: Queue) -> None:
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
    logging.info("Changing name of recording user")
    edit_name = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".username-form button.icon-rename")
        )
    )
    edit_name.click()
    driver.find_element_by_css_selector("input.username-form__input").send_keys(
        "Talked" + Keys.ENTER
    )


def join_call(driver: WebDriver, msg_queue: Queue, nextcloud_version: str) -> None:
    # Wait for the green Join Call button to appear then click it
    logging.info("Waiting for join call button to appear")
    try:
        join_call_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "button.top-bar__button.success:not(:disabled)")
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

    logging.info("Joining call")
    join_call_button.click()

    if nextcloud_version == "23":
        logging.info("Handling device checker screen")
        try:
            device_checker_join_call_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".device-checker #call_button.success")
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

        device_checker_join_call_button.click()

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


def mute_user(driver: WebDriver) -> None:
    logging.info("Muting Talked user")
    try:
        driver.find_element_by_css_selector("#mute:not(.audio-disabled)").click()
    except NoSuchElementException:
        logging.info(("Mute button wasn't found. Assuming we are already muted."))


def switch_to_speaker_view(driver: WebDriver, nextcloud_version: str) -> None:
    # Switch to speaker view
    logging.info("Switching to speaker view")

    if nextcloud_version == "23":
        driver.find_element_by_css_selector(
            ".local-media-controls button.action-item__menutoggle"
        ).click()

        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "button.action-button .icon-promoted-view",
                    )
                )
            ).click()
        except TimeoutException:
            logging.info(
                (
                    "Speaker view button wasn't found. "
                    "Assuming we are already in speaker view."
                )
            )
    else:
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
    logging.info("Loading custom CSS")

    javascript = pkgutil.get_data("talked", "static/custom_css.js")

    if javascript:
        driver.execute_script(javascript.decode("UTF-8"))
    else:
        logging.info("The custom CSS couldn't be loaded")


def graceful_shutdown(driver: WebDriver) -> None:
    logging.info("Shutting down...")
    driver.close()
    sys.exit()
