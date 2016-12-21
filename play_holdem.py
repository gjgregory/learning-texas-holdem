#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class PlayHoldem:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __setButton(self, widget, label, color):
        #change background color of widget (normal and mouseover)
        widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(color))
        widget.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.Color(color))
        #set button caption and default size
        widget.set_label(label)
        widget.set_size_request(70,70)
        widget.show()

    def __setImage(self, widget, img_filename, color):
        #change background color of widget
        widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(color))
        #assign (presumably transparent) image to widget
        image = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(img_filename)
        scaled_pixbuf = pixbuf.scale_simple(100, 150, gtk.gdk.INTERP_BILINEAR)
        image.set_from_pixbuf(scaled_pixbuf)
        image.show()
        widget.add(image)
        widget.show()

    def __setText(self, widget, text):
        buf = widget.get_buffer()
        buf.set_text(text)
        widget.set_buffer(buf)
        widget.show()


    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Machine Learning Texas Hold'em")
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(100)

        #initialize the fixed layout and all of its widgets
        self.layout = gtk.Fixed()

        self.cpuMoneyText = gtk.TextView()
        self.cpuMoneyText.set_editable(False)
        self.__setText(self.cpuMoneyText, "CPU: $10,000")

        self.cpucard1 = gtk.EventBox()
        self.__setImage(self.cpucard1, 'art_assets/black_joker.png', 'dark slate blue')
        self.cpucard2 = gtk.EventBox()
        self.__setImage(self.cpucard2, 'art_assets/black_joker.png', 'dark slate blue')

        self.deck = gtk.EventBox()
        self.__setImage(self.deck, 'art_assets/black_joker.png', 'dark slate blue')
        self.card1 = gtk.EventBox()
        self.__setImage(self.card1, 'art_assets/back.png', 'white')
        self.card2 = gtk.EventBox()
        self.__setImage(self.card2, 'art_assets/back.png', 'white')
        self.card3 = gtk.EventBox()
        self.__setImage(self.card3, 'art_assets/back.png', 'white')
        self.card4 = gtk.EventBox()
        self.__setImage(self.card4, 'art_assets/back.png', 'white')
        self.card5 = gtk.EventBox()
        self.__setImage(self.card5, 'art_assets/back.png', 'white')

        self.playercard1 = gtk.EventBox()
        self.__setImage(self.playercard1, 'art_assets/ace_of_spades.png', 'white')
        self.playercard2 = gtk.EventBox()
        self.__setImage(self.playercard2, 'art_assets/ace_of_hearts.png', 'white')

        self.buttonFold = gtk.Button()
        self.__setButton(self.buttonFold, 'FOLD', 'firebrick')
        self.buttonCheck = gtk.Button()
        self.__setButton(self.buttonCheck, 'CHECK', 'bisque 4')
        self.buttonCall = gtk.Button()
        self.__setButton(self.buttonCall, 'CALL', 'royal blue')
        self.buttonRaiseBid = gtk.Button()
        self.__setButton(self.buttonRaiseBid, 'RAISE\n    or\n  BID', 'forest green')

        self.playerMoneyText = gtk.TextView()
        self.playerMoneyText.set_editable(False)
        self.__setText(self.playerMoneyText, "You: $10,000")

        dollarsign = gtk.Label()
        dollarsign.set_markup('<span color="sea green"><span size="14000">$</span></span>')
        dollarsign.show()

        self.bidText = gtk.TextView()
        self.__setText(self.bidText, "0")
        self.bidText.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color("sea green"))
        self.bidText.set_justification(gtk.JUSTIFY_CENTER)
        self.bidText.set_size_request(70,20)

        #place all widgets into fixed layout
        self.layout.put(self.cpuMoneyText, 290, 0)
        self.layout.put(self.cpucard1, 220, 50)
        self.layout.put(self.cpucard2, 330, 50)
        self.layout.put(self.deck, 0, 250)
        self.layout.put(self.card1, 110, 250)
        self.layout.put(self.card2, 220, 250)
        self.layout.put(self.card3, 330, 250)
        self.layout.put(self.card4, 440, 250)
        self.layout.put(self.card5, 550, 250)
        self.layout.put(self.playercard1, 220, 450)
        self.layout.put(self.playercard2, 330, 450)
        self.layout.put(self.buttonFold, 0, 500)
        self.layout.put(self.buttonCheck, 105, 500)
        self.layout.put(self.buttonCall, 475, 500)
        self.layout.put(self.buttonRaiseBid, 580, 500)
        self.layout.put(self.playerMoneyText, 290, 635)
        self.layout.put(dollarsign, 567, 470)
        self.layout.put(self.bidText, 580, 475)
        self.layout.show()

        self.window.add(self.layout)
        self.window.show()

    def main(self):
        gtk.main()


if __name__ == "__main__":
    game = PlayHoldem()
    game.main()
