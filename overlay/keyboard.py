#!/usr/bin/env python
# -*- coding: utf8 -*-
import usb1
import Tkinter
import tkFont
from PIL import Image, ImageTk
import functools
import os
import sys
import threading

from steamcontroller import SteamController, SCButtons
from steamcontroller.events import EventMapper, Pos
from steamcontroller.uinput import Keys

from steamcontroller.daemon import Daemon

KEYS_MAPPING =  {
        u'1': Keys.KEY_1,
        u'2': Keys.KEY_2,
        u'3': Keys.KEY_3,
        u'4': Keys.KEY_4,
        u'5': Keys.KEY_5,
        u'6': Keys.KEY_6,
        u'7': Keys.KEY_7,
        u'8': Keys.KEY_8,
        u'9': Keys.KEY_9,
        u'0': Keys.KEY_0,
        u'ß': Keys.KEY_MINUS,
        u'<': Keys.KEY_EQUAL,
        u'q': Keys.KEY_Q,
        u'w': Keys.KEY_W,
        u'e': Keys.KEY_E,
        u'r': Keys.KEY_R,
        u't': Keys.KEY_T,
        u'z': Keys.KEY_Y,
        u'u': Keys.KEY_U,
        u'i': Keys.KEY_I,
        u'o': Keys.KEY_O,
        u'p': Keys.KEY_P,
        u'ü': Keys.KEY_LEFTBRACE,
        u'+': Keys.KEY_RIGHTBRACE,
        u'a': Keys.KEY_A,
        u's': Keys.KEY_S,
        u'd': Keys.KEY_D,
        u'f': Keys.KEY_F,
        u'g': Keys.KEY_G,
        u'h': Keys.KEY_H,
        u'j': Keys.KEY_J,
        u'k': Keys.KEY_K,
        u'l': Keys.KEY_L,
        u'ö': Keys.KEY_SEMICOLON,
        u'ä': Keys.KEY_APOSTROPHE,
        u'#': Keys.KEY_BACKSLASH,
        u'<': Keys.KEY_102ND,
        u'y': Keys.KEY_Z,
        u'x': Keys.KEY_X,
        u'c': Keys.KEY_C,
        u'v': Keys.KEY_V,
        u'b': Keys.KEY_B,
        u'n': Keys.KEY_N,
        u'm': Keys.KEY_M,
        u',': Keys.KEY_COMMA,
        u'.': Keys.KEY_DOT,
        u'-': Keys.KEY_SLASH,
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


class EventQueue(object):
    def __init__(self):
        self._lock = threading.Lock()
        self.events = []
    
    def enqueue(self, event, data={}):
        self._lock.acquire()
        self.events.append([event, data])
        self._lock.release()
    
    def dequeue(self):
        self._lock.acquire()
        if not self.events:
            self._lock.release()
            return None
        event = self.events[0]
        del self.events[0]
        self._lock.release()
        return event


class GuiEventMapper(EventMapper):
    def __init__(self, events):
        super(GuiEventMapper, self).__init__()
        self.visible = False
        self.events = events
        self.setButtonCallback(SCButtons.STEAM, self.button_pressed_callback)
        self.set_classic_buttons()
        

    def unset_button_map(self, button):
        if button in self._btn_map.keys():
            del self._btn_map[button]

    def unset_trigger_map(self, pos):
        self._trig_evts[pos] = (None, 0)

    @staticmethod
    def tigger_pressed(self, button, pressed):
        pressed_offset = 0 if pressed else 2
        pad_index = 1 if button == SCButtons.RT else 2
        self.events.enqueue(
            "<<SteamTrigger>>",
            {'serial': pad_index + pressed_offset},
        )

    @staticmethod
    def pad_move(self, pad, x, y):
        pad = 1 if pad == Pos.RIGHT else 2
        self.events.enqueue(
            "<<SteamPadMove>>",
            {'serial': pad, 'rootx': x, 'rooty': y},
        )

    @staticmethod
    def insert_whitespace(self, button, pressed):
        if pressed:
            pass#self.tk.winfo_children()[0].insert('end', ' ')

    @staticmethod
    def remove_char(self, button, pressed):
        if pressed:
            pass
            #output = self.tk.winfo_children()[0]
            #output.delete(len(output.get())-1, 'end')

    @staticmethod
    def button_pressed_callback(self, button, pressed):
        if not pressed:
            if self.visible:
                self.set_classic_buttons()
                self.visible = False
                self.events.enqueue('<<GuiHide>>')
            else:
                self.set_overlay_buttons()
                self.visible = True
                self.events.enqueue('<<GuiShow>>')


    def set_classic_buttons(self):
        self.setPadMouse(Pos.RIGHT)
        self.setPadScroll(Pos.LEFT)
        self.setStickButtons(
            [Keys.KEY_UP, Keys.KEY_LEFT, Keys.KEY_DOWN, Keys.KEY_RIGHT]
        )
        self.setTrigButton(Pos.LEFT, Keys.BTN_RIGHT)
        self.setTrigButton(Pos.RIGHT, Keys.BTN_LEFT)
        self.setButtonAction(SCButtons.LB, Keys.KEY_VOLUMEDOWN)
        self.setButtonAction(SCButtons.RB, Keys.KEY_VOLUMEUP)
        self.setButtonAction(SCButtons.A, Keys.KEY_ENTER)
        self.setButtonAction(SCButtons.B, Keys.KEY_BACKSPACE)
        self.setButtonAction(SCButtons.X, Keys.KEY_ESC)
        self.setButtonAction(SCButtons.Y, Keys.KEY_PLAYPAUSE)
        
        self.setButtonAction(SCButtons.START, Keys.KEY_NEXTSONG)
        self.setButtonAction(SCButtons.BACK, Keys.KEY_PREVIOUSSONG)
        self.setButtonAction(SCButtons.LGRIP, Keys.KEY_BACK)
        self.setButtonAction(SCButtons.RGRIP, Keys.KEY_FORWARD)
        self.setButtonAction(SCButtons.LPAD, Keys.BTN_MIDDLE)
        self.setButtonAction(SCButtons.RPAD, Keys.KEY_SPACE)

    
    def set_overlay_buttons(self):
        self.setPadButtonCallback(Pos.RIGHT, self.pad_move)
        self.setPadButtonCallback(Pos.LEFT, self.pad_move)
        self.setButtonCallback(SCButtons.LT, self.tigger_pressed)
        self.setButtonCallback(SCButtons.RT, self.tigger_pressed)
        self.setButtonCallback(SCButtons.B, self.insert_whitespace)
        self.setButtonCallback(SCButtons.A, self.remove_char)
        self.unset_trigger_map(Pos.LEFT)
        self.unset_trigger_map(Pos.RIGHT)
        self.unset_button_map(SCButtons.LB)
        self.unset_button_map(SCButtons.RB)
        self.unset_button_map(SCButtons.X)
        self.unset_button_map(SCButtons.Y)
        self.unset_button_map(SCButtons.START)
        self.unset_button_map(SCButtons.BACK)
        self.unset_button_map(SCButtons.LGRIP)
        self.unset_button_map(SCButtons.RGRIP)
        self.unset_button_map(SCButtons.LPAD)
        self.unset_button_map(SCButtons.RPAD)

class TkSteamController(SteamController):
        def __init__(self, events, tk, **kwargs):
            self.tk = tk
            self.quit = False
            self.events = events
            self.visible = False
            super(TkSteamController, self).__init__(**kwargs)

        
        def _callbackTimer(self, *args, **kwargs):
            if not self.quit:
                super(TkSteamController, self)._callbackTimer(*args, **kwargs)

        def __del__(self):
            if self._handle:
                self._handle.close()
            self.quit = True
            self.tk.quit()

        def handle_tk_events(self):
            event = self.events.dequeue()
            while event is not None:
                sys.stdout.flush()
                self.tk.event_generate(event[0], **event[1])
                event = self.events.dequeue()

        
        def run(self):
            """Fucntion to run in order to process usb events"""
            if self._handle:
                cnt=0
                try:
                    while any(x.isSubmitted() for x in self._transfer_list) and not self.quit:
                        cnt+=1
                        self._ctx.handleEvents()
                        self.handle_tk_events()
                        self.tk.update_idletasks()
                        self.tk.update()
                        if len(self._cmsg) > 0:
                            cmsg = self._cmsg.pop()
                            self._sendControl(cmsg)

                except KeyboardInterrupt:
                    del self
                    sys.exit()

                except usb1.USBErrorInterrupted:
                    pass
        
        def generate_output(self, press=True):
            pass
            #old_content = self.tk.clipboard_get()
            #self.tk.clipboard_clear()
            #string = self.tk.winfo_children()[0].get()
            #self.tk.clipboard_append(string)
            #keyboard = self._uip[1]
            #for char in string:
                #if char in KEYS_MAPPING.keys():
                    #if press:
                        #keyboard.pressEvent([KEYS_MAPPING[char]])
                    #else:
                        #keyboard.releaseEvent([KEYS_MAPPING[char]])
            #self.tk.clipboard_clear()
            #self.tk.clipboard_append(old_content)
            #if press:
                #self.tk.after(100, self.generate_output, False)
            #print keyboard._pressed
        
        def build_keyboard(self, res):
            output = Tkinter.Entry(self.tk, width=100)
            output.pack()
            lf = Tkinter.LabelFrame(self.tk, text=" keypad ", bd=3)
            lf.pack(padx=15, pady=15)
            helv36 = tkFont.Font(family='Helvetica', size=24, weight='bold')
            for row_nr, row in enumerate(KEYS):
                for key_nr, key in enumerate(row):
                    key = Tkinter.Button(
                        lf,
                        text=key,
                        width=5,
                        height=5,
                        font=helv36,
                        #command=functools.partial(virtualKeyPress, key)
                    )
                    key.grid(row=row_nr, column=key_nr)
            right = Tkinter.Label(self.tk, image=res.right_hand)
            right.pack()
            left = Tkinter.Label(self.tk, image=res.left_hand)
            left.pack()
            self.tk.withdraw()
            self.tk.bind('<<SteamTrigger>>', self.triggerPressed)
            self.tk.bind('<<GuiHide>>', self.guiHide)
            self.tk.bind('<<GuiShow>>', self.guiShow)
            self.tk.bind('<<SteamPadMove>>', self.padMove)
        
        def triggerPressed(self, evt):
            tk_index = 2 if evt.serial % 2 else 3
            label = self.tk.winfo_children()[tk_index]
            x = label.winfo_rootx()
            y = label.winfo_rooty()
            pressed = evt.serial > 2
            offset = 0 if evt.serial in (1, 3) else 36
            lf = self.tk.winfo_children()[1]
            button = _get_widget_by_pos(lf, x, y, offset)
            if button:
                if pressed:
                    button.config(relief='raised')
                    output = self.tk.winfo_children()[0]
                    output.insert('end', button.config('text')[4])
                else:
                    button.config(relief='sunken')

        def guiHide(self, evt):
            self.tk.withdraw()
            self.generate_output()
        
        def guiShow(self, evt):
            self.tk.winfo_children()[0].delete(0, 'end')
            self.tk.update()
            self.tk.deiconify()
        
        def padMove(self, evt):
            x = evt.x_root
            y = evt.y_root
            pad = Pos.RIGHT if evt.serial == 1 else Pos.LEFT
            PAD_MAX = 30000
            x = ((x + PAD_MAX) / 60000.) * self.tk.winfo_width()
            y = (1-(y + PAD_MAX) / 60000.) * self.tk.winfo_height()
            pad_index = 1 if pad == Pos.RIGHT else 2
            label = self.tk.winfo_children()[pad_index+1]
            label.place(x=x, y=y)

class SCDaemon(Daemon):
    def run(self):
        evm = GuiEventMapper()
        evm.setButtonCallback(SCButtons.STEAM, button_pressed_callback)
        sc = TkSteamController(evm, callback=evm.process)
        sc.run()




def _get_widget_by_pos(parent, x, y, offset):
    for widget in parent.winfo_children():
        w_x = widget.winfo_rootx()
        w_y = widget.winfo_rooty()
        w_h = widget.winfo_height()
        w_w = widget.winfo_width()
        if w_x <= x + offset and w_x + w_w >= x + offset and w_y <= y and w_y + w_h >= y:
            return widget
    return None




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
            events = EventQueue()
            tk = Tkinter.Tk()
            tk.overrideredirect(1)
            res = Recources()
            #build_keyboard(tk, res)
            evm = GuiEventMapper(events)
            sc = TkSteamController(events, tk, callback=evm.process)
            sc.build_keyboard(res)
            sc.run()
            #tk.mainloop()
    _main()