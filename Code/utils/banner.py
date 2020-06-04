from random import choice
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import FormattedText
from utils.color_palette import ColorSelected
from time import sleep

# Info display
info = '''               
Author: @JosueEncinar 
                                                          
Version: '0.0.1b'                         
                                                          
'''

# Thanks to http://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20

banner1 = """
__________           .______________                    
\______   \ ____   __| _/\__    ___/___ _____    _____  
 |       _// __ \ / __ |   |    |_/ __ \\__  \  /     \ 
 |    |   \  ___// /_/ |   |    |\  ___/ / __ \|  Y Y \\
 |____|_  /\___  >____ |   |____| \___  >____  /__|_|  /
        \/     \/     \/              \/     \/      \/ 
"""


def little_animation():
    msg = "redTeam >>"
    index = 0
    while True:
        print(msg[index], end="", flush=True)
        index += 1
        if index == len(msg):
          break
        sleep(0.1)

    print("\033[A")

def banner(animation=True):
    banners = [banner1]
    color = ColorSelected()
    text = FormattedText([
    (color.theme.banner, choice(banners)),
    (color.theme.primary, info)
    ])
    print_formatted_text(text)
    if animation:
      little_animation()



