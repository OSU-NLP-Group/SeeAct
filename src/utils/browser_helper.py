import pdb
import random
import socket
import subprocess

from playwright.sync_api import Playwright, expect, sync_playwright

list_us_cities = [
    ["New York", 40.77, -73.98],
    ["Log Angeles", 34.05, -118.24],
    ["Chicago", 41.88, -87.63],
    ["Houston", 29.76, -95.36],
    ["Phoneix", 33.45, -112.07],
    ["Philadelphia", 39.95, -75.17],
    ["San Antonio", 29.53, -98.47],
    ["San Diego", 32.78, -117.15],
    ["Dallas", 32.79, -96.80],
    ["San Jose", 37.30, -121.87],
    ["Austin", 30.27, -97.74],
    ["Jacksonville", 30.32, -81.66],
    ["Fort Worth", 32.75, -97.33],
    ["Columbus", 39.98, -82.98],
    ["Indianapolis", 39.77, -86.15],
    ["Charlotte", 35.23, -80.84],
    ["San Francisco", 37.77, -122.42],
    ["Seattle", 47.61, -122.33],
    ["Denver", 39.74, -104.98],
    ["Oklahoma City", 35.48, -97.53],
    ["Nashville", 36.16, -86.78],
    ["El Paso", 31.79, -106.42],
    ["Washington", 38.91, -77.01],
    ["Boston", 42.36, -71.06],
    ["Las Vegas", 36.19, -115.22],
    ["Portland", 45.52, -122.68],
    ["Detroit", 42.33, -83.05],
    ["Louisville", 38.25, -85.76],
    ["Memphis", 35.15, -90.05],
    ["Balitmore", 39.29, -76.61],
    ["Anchorage", 61.22, -149.90],
    ["Phoenix", 33.45, -112.07],
    ["Little Rock", 34.74, -92.33],
    ["Bridgeport", 41.18, -73.19],
    ["Wilmington", 39.75, -75.54],
    ["Atlanta", 33.75, -84.39],
    ["Honolulu", 21.31, -157.86],
    ["New Orleans", 29.95, -90.07],
    ["Minneapolis", 44.98, -93.27],
    ["Jackson", 32.30, -90.18],
    ["Kansas City", 39.10, -94.58],
    ["Newark", 40.73, -74.17],
    ["Salt Lake City", 40.75, -111.89],
    ["Milwaukee", 43.04, -87.96],
]

ignore_args = [
    "--enable-automation",
    "--disable-field-trial-config",
    "--disable-background-networking",
    "--enable-features=" + ("NetworkService" ",NetworkServiceInProcess"),
    "--disable-features="
    + (
        "ImprovedCookieControls"
        ",LazyFrameLoading"
        ",GlobalMediaControls"
        ",DestroyProfileOnBrowserClose"
        ",MediaRouter"
        ",DialMediaRouteProvider"
        ",AcceptCHFrame"
        ",AutoExpandDetailsElement"
        ",CertificateTransparencyComponentUpdater"
        ",AvoidUnnecessaryBeforeUnloadCheckSync"
        ",Translate"
    ),
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-back-forward-cache",
    "--disable-breakpad",
    "--disable-client-side-phishing-detection",
    "--disable-component-extensions-with-background-pages",
    "--disable-component-update",
    "--no-default-browser-check",
    "--disable-default-apps",
    "--disable-dev-shm-usage",
    "--disable-extensions",
    "--disable-features",
    "--allow-pre-commit-input",
    "--disable-hang-monitor",
    "--disable-ipc-flooding-protection",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-renderer-backgrounding",
    "--disable-sync",
    "--force-color-profile",
    "--metrics-recording-only",
    "--no-first-run",
    "--password-store",
    "--use-mock-keychain",
    "--no-service-autorun",
    "--export-tagged-pdf",
    "--no_sandbox",
]

async def normal_launch_async(playwright: Playwright):
    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
        ],
        ignore_default_args=ignore_args,
        chromium_sandbox=True,
    )
    return browser
# async def normal_launch_async(playwright: Playwright):
#     browser = await playwright.chromium.launch(
#         headless=False,
#         args=[
#             "--disable-blink-features=AutomationControlled",
#         ],
#         ignore_default_args=ignore_args,
#         chromium_sandbox=True,
#     )
#     return browser


def normal_launch(playwright: Playwright):
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
        ],
        ignore_default_args=ignore_args,
        chromium_sandbox=True,
    )
    return browser


async def normal_new_context_async(
    browser,
    storage_state=None,
    har_path=None,
    video_path=None,
    tracing=False,
record_video_size=None,
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    viewport: dict = {"width": 2048, "height": 1180},
):
    city = random.choice(list_us_cities)
    context = await browser.new_context(
        storage_state=storage_state,
        user_agent=user_agent,
        viewport=viewport,
        record_har_path=har_path,
        locale="en-US",
        record_video_dir=video_path,
        record_video_size=record_video_size,
        geolocation={"longitude": city[2], "latitude": city[1]},
    )
    if tracing:
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
    return context


def normal_new_context(browser,
    storage_state=None,
    har_path=None,
    video_path=None,
    tracing=False,
record_video_size={"width":2048,"height":1180},
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    viewport: dict = {"width": 2048, "height": 1180},
):
    city = random.choice(list_us_cities)
    context= browser.new_context(
        storage_state=storage_state,
        user_agent=user_agent,
        viewport=viewport,
        record_har_path=har_path,
        locale="en-US",
        record_video_dir=video_path,
        record_video_size=record_video_size,
        geolocation={"longitude": city[2], "latitude": city[1]},
    )
    if tracing:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
    return context




def persistent_launch(playwright: Playwright, user_data_dir: str = ""):
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
        ],
        ignore_default_args=ignore_args,
        user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 720},
    )
    return context


async def persistent_launch_async(playwright: Playwright, user_data_dir: str = ""):
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
        ],
        ignore_default_args=ignore_args,
        user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 720},
    )
    return context


def next_free_port(port=9876, max_port=9999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while port <= max_port:
        try:
            sock.bind(("", port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError("no free ports")


def connect_via_cdp(playwright: Playwright, user_data_dir: str = ""):
    # chrome_process = subprocess.Popen(
    #     [
    #         "/pw-browsers/chromium-1041/chrome-linux/chrome",
    #         "--remote-debugging-port=0",
    #         f"--user-data-dir={user_data_dir}",
    #         "--disable-blink-features=AutomationControlled",
    #     ],
    #     stderr=subprocess.STDOUT,
    #     stdout=subprocess.PIPE,
    # )
    # for line in iter(chrome_process.stdout.readline, b""):
    #     if b"DevTools listening on" in line:
    #         cdp_address = line.split()[-1].decode("utf-8")
    #         break
    cdp_address = (
        "ws://127.0.0.1:44677/devtools/browser/f41cafc7-7dfb-4b74-8e2a-d87a18751b07"
    )
    browser = playwright.chromium.connect_over_cdp(
        endpoint_url=cdp_address,
    )
    return browser


async def connect_via_cdp_async(playwright: Playwright, user_data_dir: str = ""):
    chrome_process = subprocess.Popen(
        [
            "/pw-browsers/chromium-1041/chrome-linux/chrome",
            # "--disable-dev-shm-usage",
            # "--no-startup-window",
            "--remote-debugging-port=0",
            f"--user-data-dir={user_data_dir}",
            "--disable-blink-features=AutomationControlled",
        ],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    )
    for line in iter(chrome_process.stdout.readline, b""):
        if b"DevTools listening on" in line:
            cdp_address = line.split()[-1].decode("utf-8")
            break
    # cdp_address = (
    #     "ws://127.0.0.1:9876/devtools/browser/a175e70e-2b36-4b80-ba44-2be98b1d8f3f"
    # )
    browser = await playwright.chromium.connect_over_cdp(endpoint_url=cdp_address)
    return browser, chrome_process
