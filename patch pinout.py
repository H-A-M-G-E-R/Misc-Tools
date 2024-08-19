"""
libpinout patcher tool
"""

import tkinter
import tkinter.ttk as ttk
import tkinter.messagebox
import tkinter.filedialog
import json
import os
import sys
import struct

VERSION = (0, 3, 0)

class File():
	"""
	A libpinout.so file
	"""
	
	def __init__(self, path):
		"""
		Initialise the file
		"""
		
		self.file = open(path, "rb+")
	
	def read(self, location):
		"""
		Read 32 bits from the given location
		"""
		
		self.file.seek(location, 0)
		return self.file.read(4)
	
	def patch(self, location, data):
		"""
		Write patched data to the file
		"""
		
		self.file.seek(location, 0)
		self.file.write(data)
	
	def __del__(self):
		"""
		Destroy the file
		"""
		
		self.file.close()

def patch_antitamper(f, value):
	f.patch(0x4581c, b"\x13\x00\x00\x14")
	f.patch(0x46594, b"\x04\x00\x00\x14")
	f.patch(0x468fc, b"\x3b\x00\x00\x14")
	f.patch(0x46b80, b"\x0a\x00\x00\x14")

def patch_premium(f, value):
	tkinter.messagebox.showwarning("Software copyright notice", "APKs where premium is patched should NOT be distrubuted, and this functionality is only available for users to extercise their right to modify software that they own for private use. If you do not own premium, you should delete the patched file immediately.")
	
	f.patch(0x75720, b"\x07\x00\x00\x14")
	f.patch(0x7bfb8, b"\x06\x00\x00\x14")

def patch_variable_framerate(f, value):
	# gGame->timeStep = gGame->frameTime instead of gGame->timeStep = 0.0166667
	f.patch(0x1d4190, b"\x61\x5a\x41\xbd") # gGame->timeStep = gGame->frameTime instead of gGame->timeStep = 0.0166667
	f.patch(0x1d4bac, b"\x10\x00\x00\x14") # update only once
	f.patch(0x46a40, b"\x1f\x20\x03\xd5") # remove frame limiter

PATCH_LIST = {
	"antitamper": patch_antitamper,
	"premium": patch_premium,
	"variable_framerate": patch_variable_framerate,
}

def applyPatches(location, patches):
	"""
	Apply patches to a given libpinout.so file
	"""
	
	f = File(location)
	
	ver = (f.read(0x1e0170) + f.read(0x1e0174))[:5].decode("utf-8")
	
	if (ver != '1.0.5'):
		raise Exception(f"Sorry, this doesn't seem to be version 1.0.5 for ARM64 devices. Make sure you have selected the ARM64 libpinout.so from 1.0.5 and try again.")
	
	# For each patch ...
	for p in patches:
		# ... that is actually a patch and is wanted ...
		if (not p.endswith("_val") and patches[p] == True):
			# ... do the patch, also passing (PATCHNAME) + "_val" if it exists.
			(PATCH_LIST[p])(f, patches.get(p + "_val", None))

# ==============================================================================
# ==============================================================================

class Window():
	"""
	Window thing
	"""
	
	def __init__(self, title, size, class_name = "Application"):
		"""
		Initialise the window
		"""
		
		self.window = tkinter.Tk(className = class_name)
		self.window.title(title)
		self.window.geometry(size)
		
		self.position = -25
		self.gap = 35
		
		# Main frame
		ttk.Frame(self.window)
	
	def getYPos(self, flush = False):
		self.position += self.gap if not flush else 0
		
		return self.position
	
	def label(self, content):
		"""
		Create a label
		"""
		
		label = tkinter.Label(self.window, text = content)
		label.place(x = 10, y = self.getYPos())
		
		return label
	
	def button(self, content, action):
		button = tkinter.Button(self.window, text = content, command = action)
		button.place(x = 10, y = self.getYPos())
		
		return button
	
	def textbox(self, inline = False):
		"""
		Create a textbox
		"""
		
		entry = tkinter.Entry(self.window, width = (70 if not inline else 28))
		
		if (not inline):
			entry.place(x = 10, y = self.getYPos())
		else:
			entry.place(x = 300, y = self.getYPos(True))
		
		return entry
	
	def checkbox(self, content, default = False):
		"""
		Create a tickbox
		"""
		
		var = tkinter.IntVar()
		
		tick = tkinter.Checkbutton(self.window, text = content, variable = var, onvalue = 1, offvalue = 0)
		tick.place(x = 10, y = self.getYPos())
		
		var.set(1 if default else 0)
		
		return var
	
	def main(self):
		self.window.mainloop()

def gui(default_path = None):
	w = Window(f"PinOut Binary Modification Tool v{VERSION[0]}.{VERSION[1]}.{VERSION[2]} (by Knot126 and H A M)", "510x640")
	
	w.label("This tool will let you add common patches to PinOut's main binary.")
	
	location = default_path
	
	if (not location):
		location = tkinter.filedialog.askopenfilename(title = "Pick libpinout.so", filetypes = (("Shared objects", "*.so"), ("All files", "*.*")))
	
	w.label("(Note: If you have issues typing in boxes, try clicking off and on the window first.)")
	w.label("Please select what patches you would like to apply:")
	
	antitamper = w.checkbox("Disable anti-tamper protection (required)", default = True)
	premium = w.checkbox("Enable premium by default")
	variable_framerate = w.checkbox("Enable variable framerate depending on screen refresh rate")
	
	def x():
		"""
		Callback to run when the "Patch libpinout.so!" button is clicked
		"""
		
		try:
			patches = {
				"antitamper": antitamper.get(),
				"premium": premium.get(),
				"variable_framerate": variable_framerate.get(),
			}
			
			applyPatches(location.get() if type(location) != str else location, patches)
			
			tkinter.messagebox.showinfo("Success", "Your libpinout has been patched succesfully!")
		
		except Exception as e:
			tkinter.messagebox.showerror("Error", str(e))
	
	w.button("Patch game binary!", x)
	
	w.main()

def main():
	try:
		gui(sys.argv[1] if len(sys.argv) >= 2 else None)
	except Exception as e:
		tkinter.messagebox.showerror("Fatal error", str(e))

if (__name__ == "__main__"):
	main()
