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

def unset_button_map(evm, button):
    if button in evm._btn_map.keys():
        del evm._btn_map[button]

def unset_trigger_map(evm, pos):
    evm._trig_evts[pos] = (None, 0)


def set_overlay_buttons(evm):
    evm.setPadButtonCallback(Pos.RIGHT, pad_move)
    evm.setPadButtonCallback(Pos.LEFT, pad_move)
    evm.setButtonCallback(SCButtons.LT, tigger_pressed)
    evm.setButtonCallback(SCButtons.RT, tigger_pressed)
    unset_trigger_map(evm, Pos.LEFT)
    unset_trigger_map(evm, Pos.RIGHT)
    unset_button_map(evm, SCButtons.LB)
    unset_button_map(evm, SCButtons.RB)
    unset_button_map(evm, SCButtons.A)
    unset_button_map(evm, SCButtons.B)
    unset_button_map(evm, SCButtons.X)
    unset_button_map(evm, SCButtons.Y)
    unset_button_map(evm, SCButtons.START)
    unset_button_map(evm, SCButtons.BACK)
    unset_button_map(evm, SCButtons.LGRIP)
    unset_button_map(evm, SCButtons.RGRIP)
    unset_button_map(evm,SCButtons.LPAD)
    unset_button_map(evm, SCButtons.RPAD)

def button_pressed_callback(evm, button, pressed):
    if not pressed:
        if evm.visible:
            set_classic_buttons(evm)
            evm.tk.withdraw()
            evm.visible = False
        else:
            set_overlay_buttons(evm)
            evm.tk.update()
            evm.tk.deiconify()
            evm.visible = True

def tigger_pressed(evm, button, pressed):
    if not pressed:
        pad_index = 1 if button == SCButtons.RT else 2
        label = evm.tk.winfo_children()[pad_index]
        x = label.winfo_rootx()
        y = label.winfo_rooty()
        evm.tk.event_generate(
            "<<SteamTrigger>>".format(pad_index),
            rootx=x,
            rooty=y,
            serial=pad_index,
        )

def pad_move(evm, pad, x, y):
    PAD_MAX = 30000
    x = ((x + PAD_MAX) / 60000.) * evm.tk.winfo_width()
    y = (1-(y + PAD_MAX) / 60000.) * evm.tk.winfo_height()
    pad_index = 1 if pad == Pos.RIGHT else 2
    label = evm.tk.winfo_children()[pad_index]
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
    offset = 0 if evt.serial == 1 else 36
    root = evt.widget
    lf = root.winfo_children()[0]
    button = _get_widget_by_pos(lf, x, y, offset)
    if button:
        print button.config('text')[-1]
        #button.invoke()

def _get_widget_by_pos(parent, x, y, offset):
    for widget in parent.winfo_children():
        w_x = widget.winfo_rootx()
        w_y = widget.winfo_rooty()
        w_h = widget.winfo_height()
        w_w = widget.winfo_width()
        if w_x <= x + offset and w_x + w_w >= x + offset and w_y <= y and w_y + w_h >= y:
            return widget
    return None


#def virtualKeyPress(button):
    #print button

def build_keyboard(tk, res):
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