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
    with Display(backend="xvfb", size=(1920, 1080), color_depth=24) as display:
        browser = launch_browser()
        subprocess.run(
            [
                "ffmpeg",
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
                "-i",
                display.env()["DISPLAY"],
                "-f",
                "pulse",
                "-ac",
                "2",
                "-i",
                "1",
                "-c:v",
                "libx264",
                "-crf",
                "18",
                "-preset",
                "ultrafast",
                "output.mp4",
            ]
        )
        browser.close()


def launch_browser():
    options = Options()
    options.set_preference("media.navigator.permission.disabled", True)
    options.add_argument("--kiosk")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    driver = Firefox(options=options)
    driver.get("")

    join_call = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button.top-bar__button.success")
        )
    )
    time.sleep(2)
    join_call.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".top-bar.in-call"))
    )

    page = driver.find_element_by_tag_name("body")

    page.send_keys(Keys.ESCAPE)
    page.send_keys("m")

    sidebar_close = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "a.app-sidebar__close"))
    )
    sidebar_close.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".top-bar.in-call button.top-bar__button.icon-menu-people",
            )
        )
    )
    page.send_keys("f")

    time.sleep(3)
    return driver


if __name__ == "__main__":
    main()
