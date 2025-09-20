from os import system

import colorama as col
from data.config.config_settings import DEFAULT_GUT_SETTINGS, GAME_SETTINGS


class GUT:
    def __init__(self, gut_settings=DEFAULT_GUT_SETTINGS, game_settings=GAME_SETTINGS):
        self.gut_settings = gut_settings
        self.game_settings = game_settings
        self.hl_color = col.Fore.GREEN
        self.bar_fg_color = col.Fore.BLACK
        self.bar_bg_color = col.Back.LIGHTBLACK_EX
        self.rst = col.Style.RESET_ALL

        self.standard_bar_text = "[Type \'/\' for commands, \'/h\' or \'/help\' for list of commands]"


    @staticmethod
    def stat_bar(text:str, current_value, max_value, bar_length, char, text_color_hex, bar_color_hex):
        """
        Generate status bar as string

        :param text: Basic text shown as indicator of status bar
        :param current_value: Value 1, indicating the current value, part of a full value
        :param max_value: Value 2, indicating the max value, part of a full value
        :param bar_length:
        :param char:
        :param text_color_hex:
        :param bar_color_hex:
        :return: Status bar as string
        """
        clr = Color()
        rst = clr.rst()

        # Calculate the progress as a fraction of the max_value
        progress = current_value / max_value if max_value > 0 else 0

        # Determine the length of the filled portion and the remaining portion
        filled_length = int(progress * bar_length)
        remaining_length = bar_length - filled_length

        # Construct the string
        string = (
            f'{clr.hex(text_color_hex)}{text}{rst} '  # Text part
            f'({clr.hex(bar_color_hex)}{int(current_value)}{rst}/{clr.hex(bar_color_hex)}{int(max_value)}{rst}) '  # Current/Max values
            f'[{clr.hex(bar_color_hex)}{str(char) * filled_length}{rst}'  # Filled portion of the bar
            f'{str("." * remaining_length)}]'  # Unfilled portion
        )

        return string


    def clear_screen(self) -> None:
        """
        Clears terminal screen (windows)
        :return:
        """
        system('cls' if self.gut_settings.get('os', 'windows') == 'windows' else 'clear')


    def draw_line(self, char:str|None=None) -> None:
        """
        Draw a line

        :param char: Type of character
        :return:
        """
        if char is None:
            print('' * self.gut_settings['default_line_size'])
        else:
            print(str(char) * int(self.game_settings['game_resolution'][1]))


    @staticmethod
    def draw_title(title) -> None:
        print(f"[{title}]")


    @staticmethod
    def draw_text(text) -> None:
        print(f"{text}")


    def draw_warning(self, text) -> None:
        print(f"{col.Fore.LIGHTYELLOW_EX} > [WARNING]: {text}{self.rst}")


    def draw_error(self, text) -> None:
        print(f"{col.Fore.RED} > [ERROR]: {text}{self.rst}")


    def click_text(self, text="") -> None:
        self.draw_text(text)
        input()


    def click_error(self, text) -> None:
        self.draw_error(text)
        input()


    def draw_bar_text(self, text="") -> None:
        if text == "":
            text = self.standard_bar_text

        print(f'{self.bar_bg_color} {self.bar_fg_color} {text}{self.rst}')


    def draw_box(self, width, height) -> None:
        for _ in range(height):
            self.draw_line()


    def menu_select(self, menu_options:dict, title:str|None=None, text:str|None=None, bar_text:str="", error_text:str|None=None,
                    clear_screen:bool=False, draw_line:bool=False) -> str:
        """
        Prompts user with menu, user gives back an input (type str)

        :param menu_options: Menu options to display
        :param title: Title to display
        :param text: Text to display in lines
        :param bar_text: Text in bar to display
        :param error_text: Error text to display
        :param clear_screen: Whether to clear the screen before displaying
        :param draw_line: Whether to print out a line
        :return: user_input: Returning user input of type string
        """
        # if title is not None:   TODO: why is this here? [ ] Check
        #     self.clear_screen()
        if error_text is None:
            error_text = []
        if clear_screen is True:
            self.draw_line(char="")
        if draw_line is True:
            self.draw_title(title)
        if text:
            self.draw_text(text)
        for key, value in menu_options.items():
            if 'exit' in value.lower():
                print('')
            print(f' [{self.hl_color}{key.capitalize()}{self.rst}]: {value}')

        for line in error_text:
            print(f"{col.Fore.RED}> [ERROR]: {line}{self.rst}")

        if bar_text != "":
            self.draw_bar_text(bar_text)
        user_input = input(f"> ")
        return user_input


    def display_text(self, title:str, text:str, options:dict|None=None, bar_text:str="", error_text:str|None=None) -> str:
        """
        Displays text, options to input options and error text

        :param title: Title to display
        :param text: Text to display in lines
        :param options: Menu options to display
        :param bar_text: Text in bar to display
        :param error_text: Error text to display
        :return: Returning user input of type string
        """

        if error_text is None:
            error_text = []

        self.clear_screen()
        self.draw_line()
        self.draw_title(title)

        if isinstance(text, str):
            text = text.split('\n')  # Split the text into paragraphs based on newline characters

        for paragraph in text:
            lines = paragraph.split('\n')  # Split each paragraph into lines
            for line in lines:
                print(f"{line}")  # Print each line prefixed with the desired character

        if options:
            for key, value in options.items():
                print(f'[{self.hl_color}{key.capitalize()}{self.rst}]: {value}')

        for line in error_text:
            print(f"{col.Fore.RED}> [ERROR]: {line}{self.rst}")

        self.draw_bar_text(bar_text)
        user_input = input(f"> ")
        return user_input


    @staticmethod
    def align_text(text, width, alignment='left') -> str:
        if alignment == 'l':
            return text.ljust(width)
        elif alignment == 'r':
            return text.rjust(width)
        elif alignment == 'c':
            return text.center(width)
        else:
            return f"{text}"


    @staticmethod
    def input_entry(text=""):
        input_entry = input(f" {text}> ")
        return input_entry


class Color:
    def __init__(self):
        pass


    @staticmethod
    def rst():
        return col.Style.RESET_ALL


    @staticmethod
    def bold():
        return '\x1b[1m'


    @staticmethod
    def italicize():
        return '\x1b[3m'


    @staticmethod
    def hex(hex_color, bold=False, italicize=False):
        """


        :param hex_color:
        :param bold:
        :param italicize:
        :return:
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')

        # Convert hex to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # ANSI escape sequence for colorizing text
        ansi_code = f'\x1b[38;2;{r};{g};{b}m'

        # Add ANSI escape sequences for bold and italicized text if requested
        if bold:
            ansi_code += '\x1b[1m'  # Bold
        if italicize:
            ansi_code += '\x1b[3m'  # Italicize

        return ansi_code


    @staticmethod
    def rgb_to_hex(r, g, b):
        """
        Convert RGB color values to hexadecimal color representation.

        Args:
            r (int): Red value (0-255).
            g (int): Green value (0-255).
            b (int): Blue value (0-255).

        Returns:
            str: Hexadecimal color representation.
        """
        return "#{:02x}{:02x}{:02x}".format(r, g, b)


# Example usage:
if __name__ == "__main__":
    settings = {
        'os': 'windows',
        'char': '█',
        'default_line_size': 80
    }
    gut = GUT(settings)
    gut.clear_screen()
    gut.draw_line()
    gut.draw_title('Sample Title')
    gut.draw_text('This is a sample text.')
    # gut.draw_box(20, 5)
    options = {'a': 'Option A', 'b': 'Option B', 'c': 'Option C'}
    user_input = gut.menu_select(options, title='Menu', text='Please select an option:',
                                 error_text=["File \'homework.COS\' could not be saved correctly"])
    gut.display_text('TITLE', '''Wow, look at me!
Is this working

I think so!''', options=options)
    gut.click_error("Command could not be completed successfully")
    options2 = {'1': 'START COREOS', '2': 'SETTINGS', '3': 'EXIT'}
    gut.menu_select(options2, title='COREOS GAMMA STARTUP', bar_text="[For advanced config type: \'/config\']")
