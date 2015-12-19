#!/usr/bin/env python
# -*- coding: utf8 -*-
import Tkinter
from PIL import Image, ImageTk
import functools
import os

from steamcontroller import SteamController, SCButtons
from steamcontroller.events import EventMapper, Pos
from steamcontroller.uinput import Keys

from steamcontroller.daemon import Daemon

KEYS_MAPPING =  {
        '1': Keys.KEY_1,
        '2': Keys.KEY_2,
        '3': Keys.KEY_3,
        '4': Keys.KEY_4,
        '5': Keys.KEY_5,
        '6': Keys.KEY_6,
        '7': Keys.KEY_7,
        '8': Keys.KEY_8,
        '9': Keys.KEY_9,
        '0': Keys.KEY_0,
        'ß': Keys.KEY_MINUS,
        '<': Keys.KEY_EQUAL,
        'q': Keys.KEY_Q,
        'w': Keys.KEY_W,
        'e': Keys.KEY_E,
        'r': Keys.KEY_R,
        't': Keys.KEY_T,
        'z': Keys.KEY_Y,
        'u': Keys.KEY_U,
        'i': Keys.KEY_I,
        'o': Keys.KEY_O,
        'p': Keys.KEY_P,
        'ü': Keys.KEY_LEFTBRACE,
        '+': Keys.KEY_RIGHTBRACE,
        
        'a': Keys.KEY_A,
        's': Keys.KEY_S,
        'd': Keys.KEY_D,
        'f': Keys.KEY_F,
        'g': Keys.KEY_G,
        'h': Keys.KEY_H,
        'j': Keys.KEY_J,
        'k': Keys.KEY_K,
        'l': Keys.KEY_L,
        'ö': Keys.KEY_SEMICOLON,
        'ä': Keys.KEY_APOSTROPHE,
        '#': Keys.KEY_BACKSLASH,
        '<': Keys.KEY_102ND,
        'y': Keys.KEY_Z,
        'x': Keys.KEY_X,
        'c': Keys.KEY_C,
        'v': Keys.KEY_V,
        'b': Keys.KEY_B,
        'n': Keys.KEY_N,
        'm': Keys.KEY_M,
        ',': Keys.KEY_COMMA,
        '.': Keys.KEY_DOT,
        '-': Keys.KEY_SLASH,
    }


KEYS = [
    u'1234567890ß<', u'qwertzuiopü+', u'asdfghjklöä#', u'yxcvbnm,.-',
]


class Recources(object):
    def __init__(self):
        self._base_bath = os.path.dirname(os.path.abspath(__file__))
        self._left_hand = Image.open(
            os.path.join(self._base_bath, 'right_hand.png')
        )
        self._right_hand = Image.open(
            os.path.join(self._base_bath, 'left_hand.png')
        )
        self.left_hand = ImageTk.PhotoImage(self._left_hand)
        self.right_hand = ImageTk.PhotoImage(self._right_hand)

def set_classic_buttons(evm):
    evm.setPadMouse(Pos.RIGHT)
    evm.setPadScroll(Pos.LEFT)
    evm.setStickButtons(
        [Keys.KEY_UP, Keys.KEY_LEFT, Keys.KEY_DOWN, Keys.KEY_RIGHT]
    )
    evm.setTrigButton(Pos.LEFT, Keys.BTN_RIGHT)
    evm.setTrigButton(Pos.RIGHT, Keys.BTN_LEFT)
    evm.setButtonAction(SCButtons.LB, Keys.KEY_VOLUMEDOWN)
    evm.setButtonAction(SCButtons.RB, Keys.KEY_VOLUMEUP)
    evm.setButtonAction(SCButtons.A, Keys.KEY_ENTER)
    evm.setButtonAction(SCButtons.B, Keys.KEY_BACKSPACE)
    evm.setButtonAction(SCButtons.X, Keys.KEY_ESC)
    evm.setButtonAction(SCButtons.Y, Keys.KEY_PLAYPAUSE)
    
    evm.setButtonAction(SCButtons.START, Keys.KEY_NEXTSONG)
    evm.setButtonAction(SCButtons.BACK, Keys.KEY_PREVIOUSSONG)
    evm.setButtonAction(SCButtons.LGRIP, Keys.KEY_BACK)
    evm.setButtonAction(SCButtons.RGRIP, Keys.KEY_FORWARD)
    evm.setButtonAction(SCButtons.LPAD, Keys.BTN_MIDDLE)
    evm.setButtonAction(SCButtons.RPAD, Keys.KEY_SPACE)


def insert_whitespace(evm, button, pressed):
    if pressed:
        evm.tk.winfo_children()[0].insert('end', ' ')

def remove_char(evm, button, pressed):
    if pressed:
        output = evm.tk.winfo_children()[0]
        output.delete(len(output.get())-1, 'end')


def set_overlay_buttons(evm):
    evm.setPadButtonCallback(Pos.RIGHT, pad_move)
    evm.setPadButtonCallback(Pos.LEFT, pad_move)
    evm.setButtonCallback(SCButtons.LT, tigger_pressed)
    evm.setButtonCallback(SCButtons.RT, tigger_pressed)
    evm.setButtonCallback(SCButtons.B, insert_whitespace)
    evm.setButtonCallback(SCButtons.A, remove_char)
    evm.unset_trigger_map(Pos.LEFT)
    evm.unset_trigger_map(Pos.RIGHT)
    evm.unset_button_map(SCButtons.LB)
    evm.unset_button_map(SCButtons.RB)
    evm.unset_button_map(SCButtons.X)
    evm.unset_button_map(SCButtons.Y)
    evm.unset_button_map(SCButtons.START)
    evm.unset_button_map(SCButtons.BACK)
    evm.unset_button_map(SCButtons.LGRIP)
    evm.unset_button_map(SCButtons.RGRIP)
    evm.unset_button_map(SCButtons.LPAD)
    evm.unset_button_map(SCButtons.RPAD)

def button_pressed_callback(evm, button, pressed):
    if not pressed:
        if evm.visible:
            set_classic_buttons(evm)
            evm.tk.withdraw()
            evm.visible = False
            evm.generate_output()
        else:
            set_overlay_buttons(evm)
            evm.tk.winfo_children()[0].delete(0, 'end')
            evm.tk.update()
            evm.tk.deiconify()
            evm.visible = True

def tigger_pressed(evm, button, pressed):
    pressed_offset = 0 if pressed else 2
    pad_index = 1 if button == SCButtons.RT else 2
    label = evm.tk.winfo_children()[pad_index+1]
    x = label.winfo_rootx()
    y = label.winfo_rooty()
    evm.tk.event_generate(
        "<<SteamTrigger>>".format(pad_index),
        rootx=x,
        rooty=y,
        serial=pad_index + pressed_offset,
    )

def pad_move(evm, pad, x, y):
    PAD_MAX = 30000
    x = ((x + PAD_MAX) / 60000.) * evm.tk.winfo_width()
    y = (1-(y + PAD_MAX) / 60000.) * evm.tk.winfo_height()
    pad_index = 1 if pad == Pos.RIGHT else 2
    label = evm.tk.winfo_children()[pad_index+1]
    label.place(x=x, y=y)

class GuiEventMapper(EventMapper):
    def __init__(self, tk):
        self.tk = tk
        self.visible = False
        super(GuiEventMapper, self).__init__()

    def process(self, *args, **kwargs):
        super(GuiEventMapper, self).process(*args, **kwargs)
        self.tk.update_idletasks()
        self.tk.update()

    def unset_button_map(self, button):
        if button in self._btn_map.keys():
            del self._btn_map[button]

    def unset_trigger_map(self, pos):
        self._trig_evts[pos] = (None, 0)

    def generate_output(self):
        old_content = self.tk.clipboard_get()
        self.tk.clipboard_clear()
        string = self.tk.winfo_children()[0].get()
        self.tk.clipboard_append(string)
        keyboard = self._uip[1]
        for char in string:
            if char in KEYS_MAPPING.keys():
                keyboard.pressEvent([KEYS_MAPPING[char]])
                keyboard.releaseEvent([KEYS_MAPPING[char]])
        self.tk.clipboard_clear()
        self.tk.clipboard_append(old_content)

class SCDaemon(Daemon):
    def run(self):
        evm = GuiEventMapper()
        evm.setButtonCallback(SCButtons.STEAM, button_pressed_callback)
        sc = SteamController(callback=evm.process)
        sc.run()

def contollerloop(tk):
    evm = GuiEventMapper(tk)
    evm.setButtonCallback(SCButtons.STEAM, button_pressed_callback)
    set_classic_buttons(evm)
    sc = SteamController(callback=evm.process)
    sc.run()

def triggerPressed(evt):
    x = evt.x_root
    y = evt.y_root
    pressed = evt.serial > 2
    offset = 0 if evt.serial in (1, 3) else 36
    root = evt.widget
    lf = root.winfo_children()[1]
    button = _get_widget_by_pos(lf, x, y, offset)
    if button:
        if pressed:
            button.config(relief='raised')
            output = root.winfo_children()[0]
            output.insert('end', button.config('text')[4])
        else:
            button.config(relief='sunken')


def _get_widget_by_pos(parent, x, y, offset):
    for widget in parent.winfo_children():
        w_x = widget.winfo_rootx()
        w_y = widget.winfo_rooty()
        w_h = widget.winfo_height()
        w_w = widget.winfo_width()
        if w_x <= x + offset and w_x + w_w >= x + offset and w_y <= y and w_y + w_h >= y:
            return widget
    return None


def build_keyboard(tk, res):
    output = Tkinter.Entry(tk, width=100)
    output.pack()
    lf = Tkinter.LabelFrame(tk, text=" keypad ", bd=3)
    lf.pack(padx=15, pady=15)
    for row_nr, row in enumerate(KEYS):
        for key_nr, key in enumerate(row):
            key = Tkinter.Button(
                lf,
                text=key,
                width=5,
                height=5,
                #command=functools.partial(virtualKeyPress, key)
            )
            key.grid(row=row_nr, column=key_nr)
    right = Tkinter.Label(tk, image=res.right_hand)
    right.pack()
    left = Tkinter.Label(tk, image=res.left_hand)
    left.pack()
    tk.withdraw()
    tk.bind('<<SteamTrigger>>', triggerPressed)

if __name__ == '__main__':
    import argparse

    def _main():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('command', type=str, choices=['start', 'stop', 'restart', 'debug'])
        args = parser.parse_args()
        daemon = SCDaemon('/tmp/steamcontroller.pid')

        if 'start' == args.command:
            daemon.start()
        elif 'stop' == args.command:
            daemon.stop()
        elif 'restart' == args.command:
            daemon.restart()
        elif 'debug' == args.command:
            tk = Tkinter.Tk()
            res = Recources()
            build_keyboard(tk, res)
            tk.after(100, contollerloop, tk)
            tk.mainloop()
            
    _main()