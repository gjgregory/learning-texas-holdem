#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class PlayHoldem:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __set_image(self, widget, img_filename):
        #change background color of widget
        colormap = widget.get_colormap()
        color = colormap.alloc_color("white")
        style = widget.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = color
        widget.set_style(style)

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


    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(200)

        self.card1 = gtk.Button()
        self.__set_image(self.card1, 'art_assets/ace_of_spades.png')
        self.card1.show()



        self.window.add(self.card1)
        self.window.show()

    def main(self):
        gtk.main()


if __name__ == "__main__":
    game = PlayHoldem()
    game.main()
