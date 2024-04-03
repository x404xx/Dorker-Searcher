import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import requests
from user_agent import generate_user_agent

from .printer import Printer
from .prompter import Prompter


class ProxyChecker(Prompter, Printer):
    """Proxies updated every 30 minutes"""

    CHECK_URL = "https://www.bing.com/"
    PROXY_URL = (
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
    )
    GITHUB_API_URL = "https://api.github.com/repos/monosans/proxy-list/commits"

    def __init__(self):
        self.session = requests.Session()
        self.live_proxies = set()
        self.dead_count = 0

    def __del__(self):
        self.session.close()

    def start_timer(self, started_time: float):
        return (
            f"[green1]{round(elapsed * 1000)}[/] miliseconds!"
            if (elapsed := round((time.time() - started_time), 2)) < 1
            else (
                f"[green1]{elapsed}[/] seconds!"
                if elapsed < 60
                else f"[green1]{int(elapsed // 60)}[/] minutes [green1]{int(elapsed % 60)}[/] seconds!"
            )
        )

    def _get_commit_time(self):
        if (response := self.session.get(self.GITHUB_API_URL)).status_code == 200:
            if commits := response.json():
                return commits[0]["commit"]["author"]["date"]
        return None

    def _calculate_time_difference(self, commit_time: str):
        commit_datetime = datetime.strptime(commit_time, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
        current_datetime = datetime.now(timezone.utc)
        time_difference = current_datetime - commit_datetime
        minutes, seconds = divmod(time_difference.total_seconds(), 60)
        return (
            f"Updated {int(minutes)} minutes ago"
            if int(minutes) > 0
            else f"Updated {int(seconds)} seconds ago"
        )

    def _convert_commit_time(self):
        if commit_time := self._get_commit_time():
            return self._calculate_time_difference(commit_time)
        return "Failed to retrieve commit time"

    def _fetch_proxy_list(self):
        response = self.session.get(self.PROXY_URL)
        proxy_list = [proxy.strip() for proxy in response.text.splitlines()]
        self.print_proxy_found(proxy_list, self._convert_commit_time())
        random.shuffle(proxy_list)
        return proxy_list

    def get_proxy_limit(self):
        proxy_list = self._fetch_proxy_list()
        limiter = self.proxy_limiter()
        proxy_limit = proxy_list if not limiter.strip() else proxy_list[: int(limiter)]
        return proxy_limit

    def working_proxy(self, proxy_limit: list, worker: int):
        proxy_started = time.time()
        self._start_checking(proxy_limit, worker)
        self.print_checking_proxy_time_taken(self.start_timer(proxy_started))
        return list(self.live_proxies)

    def _check_proxy(self, proxy: str):
        try:
            user_agent = str(generate_user_agent())
            proxies = {"http": proxy, "https": proxy}
            response = self.session.get(
                self.CHECK_URL,
                headers={"User-Agent": user_agent},
                proxies=proxies,
                timeout=5,
            )
            if 200 <= response.status_code <= 299:
                self.live_proxies.add(proxy)
            else:
                self.dead_count += 1
        except requests.RequestException:
            self.dead_count += 1

        self.print_live_dead_proxy(self.live_proxies, self.dead_count)

    def _start_checking(self, proxy_limit: list, worker: int):
        with ThreadPoolExecutor(max_workers=worker) as executor:
            executor.map(self._check_proxy, proxy_limit)
