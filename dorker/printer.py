from threading import Lock
from typing import Callable

from .console import console


class Printer:
    @staticmethod
    def print_save_success():
        console.print(f"\n[yellow]Output saved successfully.[/]\n")

    @staticmethod
    def print_no_output():
        console.print(f"\n[yellow]No output to save.[/]\n")

    @staticmethod
    def print_connection_issues():
        console.clear()
        console.print(
            f"[red1]Every live proxy has issues with connections. [bold white]Now trying with a new proxies...[/]"
        )

    @staticmethod
    def print_not_enough_proxies():
        console.print(
            f"[yellow]Live proxies is not enough for url amount.[/] [bold white]Adding more proxies..[/]"
        )

    @staticmethod
    def print_live_dead_proxy(live_proxies: set, dead_count: int):
        console.print(
            f"[white]Live[/]: ([green1]{len(live_proxies)}[/]) [white]Dead[/]: ([red1]{dead_count}[/])",
            end="\r",
        )

    @staticmethod
    def print_proxy_found(proxy_list: list, commits: Callable):
        console.print(
            f"\nFound [green1]{len(proxy_list)}[/] [blue1]HTTP|SOCKS4|SOCKS5[/] mixed proxies! - [red1]([bold white]{commits}[red1])[/]"
        )

    @staticmethod
    def print_checking_proxy_time_taken(start_timer: Callable):
        console.print(f"\n\n[yellow]Checking proxy time taken[/]: {start_timer}\n")

    @staticmethod
    def print_color_list(color_list: list):
        console.print(f"\nStarted: {', '.join(color_list)}\n")

    @staticmethod
    def print_proxy_ua(lock: Lock, info: bool, proxy: str, user_agent: str):
        if info:
            with lock:
                console.print(
                    f"Proxy: [green1]{proxy}[/] | User-Agent: [medium_purple1]{user_agent}[/]"
                )

    @staticmethod
    def print_urls(all_url: set, proxy: str, amount: int, start_timer: Callable):
        console.clear()
        console.print(f"Proxy used: {proxy}\n")
        for idx, url in enumerate(list(all_url)[:amount], start=1):
            console.print(f"[bold white]{idx}. [pale_green3]{url}[/]")

        console.print(f"\n[yellow]Searching time taken[/]: {start_timer}")

    @staticmethod
    def print_current_live_proxy(amount: int, live_proxies: list):
        console.print(
            f"\n[bold white]Current live proxies: [deep_pink3]{len(live_proxies)}[/] | Required >= [deep_pink3]{amount}[/]"
        )

    @staticmethod
    def print_exception(lock: Lock, info: bool, exc: Exception):
        if info:
            with lock:
                console.print(f"Exception: [red1]{type(exc).__name__}[/]")

    @staticmethod
    def print_no_result_found(message: str):
        console.print(f"\n:no_entry: [red1]{message}[/]\n")
