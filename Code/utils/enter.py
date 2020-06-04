try:
    from pynput.keyboard import Key, Controller
    PYINPUT = True
except:
    PYINPUT = False

# TODO: CHECK
def enter_input():
    if PYINPUT:
        keyboard = Controller()
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)