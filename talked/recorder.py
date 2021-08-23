import time
import subprocess
import logging
import sys
import pkgutil
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
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
from talked import config

msg_queue = None


def start(token, queue, recording):
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
    ) as display:
        logging.info("Starting browser")
        logging.info(call_link)
        browser = launch_browser(call_link)
        logging.info("Starting ffmpeg process")
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
                f"{config['video_width']}x{config['video_height']}",
                "-framerate",
                str(config["framerate"]),
                "-draw_mouse",
                "0",
                "-thread_queue_size",
                str(config["video_thread_queue_size"]),
                "-i",
                display.env()["DISPLAY"],
                "-f",
                "pulse",
                "-ac",
                "2",
                "-channel_layout",
                "stereo",
                "-thread_queue_size",
                str(config["audio_thread_queue_size"]),
                "-i",
                "0",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                config["audio_codec"],
                "-b:a",
                config["audio_bitrate"],
                "-c:v",
                config["video_codec"],
                "-crf",
                str(config["crf"]),
                "-preset",
                config["encoding_preset"],
                "-threads",
                str(config["encoding_threads"]),
                (
                    f"{config['recording_dir']}/"
                    f"{time.strftime('%Y%m%dT%H%M%S')}_output.mp4"
                ),
            ]
        )
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


def launch_browser(call_link):
    logging.info("Configuring browser options")
    options = Options()
    options.set_preference("media.navigator.permission.disabled", True)
    options.set_preference("privacy.webrtc.legacyGlobalIndicator", False)
    options.set_preference("full-screen-api.warning.timeout", 0)
    options.add_argument("--kiosk")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

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

    switch_to_speaker_view(driver)

    close_sidebar(driver)

    # Go fullscreen
    page.send_keys("f")

    logging.info("Loading custom CSS")
    load_custom_css(driver)

    # Give it some time to properly connect to participants.
    time.sleep(5)
    return driver


def assemble_call_link(base_url, token):
    return base_url + "/index.php/call/" + token


def is_valid_talk_room(driver):
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


def switch_to_speaker_view(driver):
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


def close_sidebar(driver):
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
                ".top-bar.in-call button.top-bar__button.icon-menu-people",
            )
        )
    )


def close_toasts(driver):
    while True:
        logging.info("Closing toast")
        try:
            driver.find_element_by_css_selector("span.toast-close").click()
        except NoSuchElementException:
            logging.info("No more open toasts")
            break


def load_custom_css(driver):
    javascript = pkgutil.get_data("talked", "static/custom_css.js").decode("UTF-8")
    driver.execute_script(javascript)


def graceful_shutdown(driver):
    logging.info("Shutting down...")
    driver.close()
    sys.exit()
