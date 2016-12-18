#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class PlayHoldem:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(200)

        self.button = gtk.Button("Play Game")
        self.button.set_size_request(100,100)
        self.window.add(self.button)
        self.button.show()
        self.window.show()

    def main(self):
        gtk.main()


if __name__ == "__main__":
    game = PlayHoldem()
    game.main()
