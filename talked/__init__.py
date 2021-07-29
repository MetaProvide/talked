import time
import subprocess

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

from pyvirtualdisplay import Display


def main():
    # Make sure an instance of Pulseaudio is running.
    subprocess.run(["pulseaudio", "--start"])

    with Display(backend="xvfb", size=(1920, 1080), color_depth=24) as display:
        browser = launch_browser()
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
        print("Recording has started")
        time.sleep(30)
        ffmpeg.terminate()
        browser.close()


def launch_browser():
    options = Options()
    options.set_preference("media.navigator.permission.disabled", True)
    options.set_preference("privacy.webrtc.legacyGlobalIndicator", False)
    options.set_preference("full-screen-api.warning.timeout", 0)
    options.add_argument("--kiosk")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    driver = Firefox(options=options)
    driver.get("")

    # Change the name of the recording user
    change_name_of_user(driver)

    # Wait for the green Join Call button to appear then click it
    join_call = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button.top-bar__button.success")
        )
    )
    time.sleep(2)
    join_call.click()

    # Wait for the call to initiate
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".top-bar.in-call"))
    )

    # Get page body to send keyboard shortcuts
    page = driver.find_element_by_tag_name("body")

    # Press escape to remove focus from chat.
    page.send_keys(Keys.ESCAPE)
    # Press m to mute the microphone, if there is one attached.
    page.send_keys("m")

    # Switch to speaker view
    speaker_view = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".top-bar.in-call button.icon-promoted-view")
        )
    )
    speaker_view.click()

    # Close the sidebar
    sidebar_close = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "a.app-sidebar__close"))
    )
    sidebar_close.click()

    # Wait for sidebar to close, then go fullscreen
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".top-bar.in-call button.top-bar__button.icon-menu-people",
            )
        )
    )
    page.send_keys("f")

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


def load_custom_css(driver):
    with open("custom_css.js") as f:
        javascript = "".join(line.strip() for line in f)
    driver.execute_script(javascript)


if __name__ == "__main__":
    main()
