from .console import prompt


class Prompter:
    @staticmethod
    def proxy_limiter():
        return prompt.ask(
            "[blue]How many proxies should be checked[/] (Press [cyan]ENTER[/] to skip limit)"
        )

    @staticmethod
    def warning_exists():
        return (
            prompt.ask(
                f"\n[red1]Warning:[/] [medium_spring_green]Output file already exists. Do you want to overwrite it? (y/n)"
            ).lower()
            == "y"
        )

    @staticmethod
    def dorker():
        return prompt.ask("[blue]Dork[/]")

    @staticmethod
    def how_many_urls():
        return int(prompt.ask("[blue]How many URLs[/]"))

    @staticmethod
    def concurrent_worker():
        return int(
            prompt.ask(
                "[blue]How many workers[/] (Press [cyan]ENTER[/] for default 50)"
            )
            or 50
        )

    @staticmethod
    def get_info():
        return prompt.ask("[blue]Do want to get info?[/] (y/n)").lower() == "y"

    @staticmethod
    def get_filename():
        return prompt.ask("\n[blue]Your filename[/] (Without Extension)")

    @staticmethod
    def new_filename():
        return prompt.ask("[blue]Enter a new filename[/] (Without Extension)")
