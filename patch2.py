"""
libsmashhit patcher tool
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
	A libsmashhit.so file
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
	f.patch(0x47130, b"\x1f\x20\x03\xd5")
	f.patch(0x474b8, b"\x3e\xfe\xff\x17")
	f.patch(0x47464, b"\x3a\x00\x00\x14")
	f.patch(0x47744, b"\x0a\x00\x00\x14")
	f.patch(0x4779c, b"\x1f\x20\x03\xd5")
	f.patch(0x475b4, b"\xff\xfd\xff\x17")
	f.patch(0x46360, b"\x13\x00\x00\x14")

def patch_bosses(f, value):
	f.patch(0x6b84c, b"\x0f\x00\x00\x14")

def patch_training_rng(f, value):
	f.patch(0x190c00, b"\x3c\x00\x00\x14")

def patch_training_ballcount(f, value):
	f.patch(0x6ba5c, b"\x06\x00\x00\x14")

PATCH_LIST = {
	"antitamper": patch_antitamper,
	"bosses": patch_bosses,
	"training_rng": patch_training_rng,
	"training_ballcount": patch_training_ballcount,
}

def applyPatches(location, patches):
	"""
	Apply patches to a given libsmashhit.so file
	"""
	
	f = File(location)
	
	ver = (f.read(0x1f38a0) + f.read(0x1f38a4))[:5].decode("utf-8")
	
	if (ver != '1.4.2' and ver != '1.4.3'):
		raise Exception(f"Sorry, this doesn't seem to be version 1.4.2 or version 1.4.3 for ARM64 devices. Make sure you have selected the ARM64 libsmashhit.so from 1.4.2 or 1.4.3 and try again.")
	
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
	w = Window(f"Smash Hit Binary Modification Tool v{VERSION[0]}.{VERSION[1]}.{VERSION[2]} (by Knot126 and H A M)", "510x640")
	
	w.label("This tool will let you add common patches to Smash Hit's main binary.")
	
	location = default_path
	
	if (not location):
		location = tkinter.filedialog.askopenfilename(title = "Pick libsmashhit.so", filetypes = (("Shared objects", "*.so"), ("All files", "*.*")))
	
	w.label("(Note: If you have issues typing in boxes, try clicking off and on the window first.)")
	w.label("Please select what patches you would like to apply:")
	
	antitamper = w.checkbox("Disable anti-tamper protection (required)", default = True)
	bosses = w.checkbox("Enable boss rooms in training/classic modes")
	training_rng = w.checkbox("Enable random room layouts in training mode")
	training_ballcount = w.checkbox("Remove ball count cap of 500 in training mode")
	
	def x():
		"""
		Callback to run when the "Patch libsmashhit.so!" button is clicked
		"""
		
		try:
			patches = {
				"antitamper": antitamper.get(),
				"bosses": bosses.get(),
				"training_rng": training_rng.get(),
				"training_ballcount": training_ballcount.get(),
			}
			
			applyPatches(location.get() if type(location) != str else location, patches)
			
			tkinter.messagebox.showinfo("Success", "Your libsmashhit has been patched succesfully!")
		
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
