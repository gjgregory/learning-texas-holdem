#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class PlayHoldem:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __set_button_image(self, widget, img_filename, color):
        #change background color of widget
        widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("white"))

        #initialize box and image
        box = gtk.HBox(False, 0)
        box.set_border_width(5)
        image = gtk.Image()

        #build and re-scale pixbuf
        pixbuf = gtk.gdk.pixbuf_new_from_file(img_filename)
        scaled_pixbuf = pixbuf.scale_simple(80, 120, gtk.gdk.INTERP_BILINEAR)

        #set image into box and add box to button
        image.set_from_pixbuf(scaled_pixbuf)
        box.pack_start(image, False, False, 0)
        image.show()
        widget.add(box)
        box.show()
        widget.show()

    def __set_image(self, widget, img_filename, color):
        #change background color of widget
        widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(color))

        image = gtk.Image()
        #build and re-scale pixbuf
        pixbuf = gtk.gdk.pixbuf_new_from_file(img_filename)
        scaled_pixbuf = pixbuf.scale_simple(100, 140, gtk.gdk.INTERP_BILINEAR)
        image.set_from_pixbuf(scaled_pixbuf)
        image.show()
        widget.add(image)
        widget.show()


    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Machine Learning Texas Hold'em")
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(100)

        self.layout = gtk.Fixed()

        #self.card1 = gtk.Button()
        #self.__set_button_image(self.card1, 'art_assets/ace_of_spades.png')

        self.cpucard1 = gtk.EventBox()
        self.__set_image(self.cpucard1, 'art_assets/black_joker.png', 'purple')
        self.cpucard2 = gtk.EventBox()
        self.__set_image(self.cpucard2, 'art_assets/black_joker.png', 'purple')

        self.deck = gtk.EventBox()
        self.__set_image(self.deck, 'art_assets/black_joker.png', 'purple')
        self.card1 = gtk.EventBox()
        self.__set_image(self.card1, 'art_assets/back.png', 'white')
        self.card2 = gtk.EventBox()
        self.__set_image(self.card2, 'art_assets/back.png', 'white')
        self.card3 = gtk.EventBox()
        self.__set_image(self.card3, 'art_assets/back.png', 'white')
        self.card4 = gtk.EventBox()
        self.__set_image(self.card4, 'art_assets/back.png', 'white')
        self.card5 = gtk.EventBox()
        self.__set_image(self.card5, 'art_assets/back.png', 'white')

        self.playercard1 = gtk.EventBox()
        self.__set_image(self.playercard1, 'art_assets/ace_of_spades.png', 'white')
        self.playercard2 = gtk.EventBox()
        self.__set_image(self.playercard2, 'art_assets/ace_of_hearts.png', 'white')


        self.layout.put(self.cpucard1, 220, 0)
        self.layout.put(self.cpucard2, 330, 0)
        self.layout.put(self.deck, 0, 200)
        self.layout.put(self.card1, 110, 200)
        self.layout.put(self.card2, 220, 200)
        self.layout.put(self.card3, 330, 200)
        self.layout.put(self.card4, 440, 200)
        self.layout.put(self.card5, 550, 200)
        self.layout.put(self.playercard1, 220, 400)
        self.layout.put(self.playercard2, 330, 400)
        self.layout.show()

        self.window.add(self.layout)
        self.window.show()

    def main(self):
        gtk.main()


if __name__ == "__main__":
    game = PlayHoldem()
    game.main()
