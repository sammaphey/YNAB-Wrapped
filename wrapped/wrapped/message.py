from typing import Any, Callable, Dict, List, Tuple

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt


class Message:
    def __init__(self, s: str, with_print: bool = True):
        """
        Display a message to the user.

        :param s: The message to display
        :param with_print: whether or not to immediately print to standard out, defaults to True
        """
        self.s = s
        self.with_print = with_print
        self.wrap = ""

    def message(self) -> str:
        """
        Display some message.

        :return: The `rich` formatted message
        """
        self.s = f"\n[bold {self.wrap}] {self.s} [/bold {self.wrap}]"
        if self.with_print:
            print(self.s)
        return self.s

    def info(self) -> str:
        """
        Display some info message.

        :return: The `rich` formatted message
        """
        self.wrap = "blue"
        return self.message()

    def success(self) -> str:
        """
        Display some success message.

        :return: The `rich` formatted message
        """
        self.wrap = "green"
        return self.message()

    def error(self) -> str:
        """
        Display some error message.

        :return: The `rich` formatted message
        """
        self.wrap = "red"
        return self.message()

    def help(self) -> str:
        """
        Display some help message.

        :return: The `rich` formatted message
        """
        self.wrap = "purple"
        return self.message()

    def error_confirmation(self, default: bool = False) -> bool:
        """
        Present an error confirmation to the user.

        Typically done when an exception needs to be handled given user input.

        :param default: The default choice, defaults to False
        :return: True if the choice is yes, False otherwise
        :rtype: bool
        """
        self.with_print = False
        return Confirm.ask(self.error(), default=default)

    def confirmation(self, default: bool = False) -> bool:
        """
        Confirm with the user.

        :param default: The default choice, defaults to False
        :return: True if the choice is yes, False otherwise
        """
        self.with_print = False
        return Confirm.ask(self.info(), default=default)

    def prompt(self) -> str:
        """
        Prompt the user for some data.

        :return: The result of the user input
        """
        self.with_print = False
        return Prompt.ask(self.info())

    def password(self) -> str:
        """
        Get a password input from the user.

        :return: The password
        """
        self.with_print = False
        return Prompt.ask(self.info(), password=True)

    def link(self, link: str) -> str:
        """
        Present a lik to the user.

        > Note: Does not work in VSCode as of this moment.

        :param link: The link to navigate to.
        :return: The text as created by the message.
        """
        self.s = f"[link={link}]{self.s}[/link]"
        return self.s

    def choice(
        self,
        choices: List[str] = None,
        default: str = None,
        dispatch: Dict[str, Tuple[str, Callable]] = None,
        dispatch_kwargs: Tuple[Any] = None,
    ) -> str:
        """
        Present a list of choices to the user to pick from.

        > Example Usage
        ```python
        dispatch = {
            "C": (
                "This CLI is Cool",
                lambda **kwargs: Message("Yeah I think so too 😎").success()
            ),
            "N": (
                "This CLI is Not Cool",
                lambda **kwargs: Message("No I think you are wrong 😠").error()
            ),
            "V": (
                "This CLI is Very Cool",
                lambda **kwargs: Message("Wow! don't get ahead of yourself though... 😊").success()
            ),
            "NC": (
                "This CLI is Very Not Cool",
                lambda **kwargs: Message("Yeah, you are probably right... 😢").error()
            ),
        }

        arg = "some kwarg to give to the dispatch function"
        Message("Looks like you have a list of choices, what do you want to say?").choice(
            dispatch=dispatch,
            dispatch_kwargs={"some": arg}
        )
        ```

        :param choices: A list of choices to pick from, defaults to None
        :param default: A choice to pick from, must be in the list of choices, defaults to None
        :param dispatch: A dispatch dictionary to handle functions that may occur given a choice,
            defaults to None
        :param dispatch_kwargs: kwargs to give the dispatch functions, defaults to None
        :return:
            If no dispatch then return the choice input
            Otherwise return the result of the dispatch function
        """
        self.with_print = False
        help_ = ""
        if dispatch:
            help_ = Message(
                "[  \n\t"
                f"{f'{chr(10)}{chr(9)}'.join([f'{dispatch[d][0]} ({d})' for d in dispatch])}"
                "\n  ]\n",
                with_print=False,
            ).help()
        result = Prompt.ask(
            f"{self.info()}\n\nHow shall I proceed?{help_}",
            choices=choices or list(dispatch.keys()),
            default=default or next(iter(dispatch)),
        )
        if dispatch:
            return dispatch[result][1](**(dispatch_kwargs or {}))
        return result


def add_progress(cb: Callable[[None], Any], description="Working...") -> Any:
    """
    Add a progress bar while waiting for some long process that occurs in the given callback.

    > Example Usage
    ```python
    add_progress(lambda: some_function_that_is_slow(), "I am a slow function 🚆...")
    ```

    :param cb: A callback function to run in the context of rich progress.
    :param description: A description to present during the progress, defaults to "Working..."
    :return: The result of the callback function.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=description, total=None)
        return cb()
