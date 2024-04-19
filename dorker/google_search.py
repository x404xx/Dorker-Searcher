import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

from .console import console
from .proxier import ProxyChecker


class DorkSearch(ProxyChecker):
    BASE_URL = "https://www.google.com/search"

    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.hit_proxy = []
        self.found_urls = set()

    def _send_request(self, dork: str, amount: int, proxies: dict, user_agent: str):
        response = self.session.get(
            self.BASE_URL,
            headers={"User-Agent": user_agent},
            params={"q": dork, "num": amount + 3, "hl": "en"},
            proxies=proxies,
            timeout=15,
        )
        response.raise_for_status()
        return response

    def _open_file(self, results_dict: dict, file_path: str):
        with open(file_path, "w") as file:
            json.dump(results_dict, file, indent=4)
        self.print_save_success()

    def _save_to_file(self, dork: str, file_name: str):
        if not self.found_urls:
            self.print_no_output()
            return
        results_dict = {dork: list(self.found_urls)}
        file_path = f"{file_name}.json"
        self._write_results_to_file(results_dict, file_path)

    def _write_results_to_file(self, results_dict: dict, file_path: str):
        output_folder = "output"
        os.makedirs(output_folder, exist_ok=True)
        file_path = os.path.join(output_folder, file_path)
        if os.path.exists(file_path):
            overwrite = self.warning_exists()
            if not overwrite:
                file_name = self.new_filename()
                file_path = os.path.join(output_folder, f"{file_name}.json")
        self._open_file(results_dict, file_path)

    def _handle_no_result(self, response: requests.Response):
        soup = BeautifulSoup(response.content, "lxml")
        no_result = soup.select_one(".card-section > p:nth-child(1)")
        return no_result.get_text(strip=True) if no_result else None

    def _handle_urls(self, response: requests.Response):
        soup = BeautifulSoup(response.content, "lxml")
        href_list = [link.get("href") for link in soup.select("div.yuRUbf a[href]")]
        filtered_urls = [
            (
                parse_qs(urlparse(link, "http").query)["q"][0]
                if link.startswith("/url?")
                else link
            )
            for link in href_list
            if urlparse(link, "http").netloc
            and "google" not in urlparse(link, "http").netloc
            and "wikipedia" not in urlparse(link, "http").netloc
        ]
        return filtered_urls

    def _color_template(
        self, dork: str, amount: int, worker: int, proxy_limit: list, info: bool
    ):
        color_template = f"[pale_green3]{{}}[red1]([bold white]{{}}[red1])[/]"
        start_mapping = {
            "Dork": dork,
            "Amount": amount,
            "Worker": worker,
            "Limiter": len(proxy_limit),
            "Info": info,
        }
        color_list = [
            color_template.format(key, value) for key, value in start_mapping.items()
        ]
        return color_list

    def _is_enough_working_proxy(
        self, dork: str, amount: int, worker: int, info: bool, is_stop_iteration=False
    ):
        if is_stop_iteration:
            self.live_proxies.clear()
            self.dead_count = 0

        proxy_limit = self.get_proxy_limit()
        color_list = self._color_template(dork, amount, worker, proxy_limit, info)
        self.print_color_list(color_list)
        working_proxy = self.working_proxy(proxy_limit, worker)

        while len(working_proxy) < amount:
            console.clear()
            self.print_color_list(color_list)
            self.print_not_enough_proxies()
            proxy_limit = self.get_proxy_limit()
            color_list = self._color_template(dork, amount, worker, proxy_limit, info)
            self.print_current_live_proxy(amount, working_proxy)
            self.print_color_list(color_list)
            working_proxy = self.working_proxy(proxy_limit, worker)
            if len(working_proxy) == amount:
                break

        return iter(working_proxy)

    def _process_completed(self, futures: list, info: bool, proxy: str):
        for future in as_completed(futures):
            try:
                if not (response := future.result()):
                    continue
                if no_result := self._handle_no_result(response):
                    self.print_no_result_found(no_result)
                    sys.exit(0)
                if urls := self._handle_urls(response):
                    self.found_urls.update(urls)
                    self.hit_proxy.append(proxy)
            except requests.RequestException as exc:
                self.print_exception(self.lock, info, exc)

    def _search_dorks(
        self,
        dork: str,
        amount: int,
        worker: int,
        info: bool,
        proxy=None,
        search_started=None,
    ):
        proxy_iterator = self._is_enough_working_proxy(dork, amount, worker, info)
        while len(self.found_urls) < amount:
            with ThreadPoolExecutor(max_workers=worker) as executor:
                futures = []
                for _ in range(amount):
                    try:
                        proxy = str(next(proxy_iterator))
                    except StopIteration:
                        self.print_connection_issues()
                        proxy_iterator = self._is_enough_working_proxy(
                            dork, amount, worker, info, True
                        )

                    user_agent = str(generate_user_agent())
                    proxies = {"http": proxy, "https": proxy}

                    self.print_proxy_ua(self.lock, info, proxy, user_agent)
                    future = executor.submit(
                        self._send_request,
                        dork,
                        amount,
                        proxies,
                        user_agent,
                    )
                    futures.append(future)

                search_started = time.time()
                self._process_completed(futures, info, proxy)

        self.print_urls(
            self.found_urls, self.hit_proxy, amount, self.start_timer(search_started)
        )

    def start_program(
        self,
        dork: str = None,
        worker: int = None,
        amount: int = None,
        file_name: str = None,
        info=False,
    ):

        dork = dork or self.dorker()
        amount = amount or self.how_many_urls()
        worker = worker or self.concurrent_worker()
        info = info or self.get_info()
        self._search_dorks(dork, amount, worker, info)
        file_name = file_name or self.get_filename()
        self._save_to_file(dork, file_name)
