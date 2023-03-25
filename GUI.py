# front end UI

import data

import pygame
from pygame.locals import *
pygame.font.init()

from tkinter.filedialog import asksaveasfilename as tksave
from tkinter.filedialog import askopenfilename as tkopen
from tkinter import Tk

root = Tk()
root.withdraw()

label_height = 50
padding = 20
label_height_total = label_height + padding

box_width = 450

font = pygame.font.SysFont('Cascadia Mono Regular', label_height*4//5)
sfont = pygame.font.SysFont('Segoe UI', label_height*4//5)
bfont = pygame.font.SysFont('Segoe UI', label_height*4//5)
# bfont = pygame.font.Font('SegoeUIB.ttf', label_height*4//5)

c = type('c', (), {'__matmul__': (lambda s, x: (*x.to_bytes(3, 'big'),)), '__sub__': (lambda s, x: (x&255,)*3)})()
bg = c@0xfff8fe
fg = c@0x080310

hint_colour = c--80

box_colour = c--20
selected_box_colour = c--42
hover_box_colour = c--32

button_colour = c@0x80e040
hover_button_colour = c@0xa0f080
selected_button_colour = c@0x80c040

divider_colour = c--25

# box_states
NONE, HOVER, SELECTED, *_ = range(4)

fps = 144

w, h = res = (1800, 900)

def updateStat(msg = None, update = True):
	rect = (0, h-20, w, 21)
	display.fill(c-0, rect)

	tsurf = sfont.render(msg or f'{pos}', True, c--1)
	display.blit(tsurf, (5, h-20))

	if update: pygame.display.update(rect)

def resize(size):
	global w, h, res, display
	w, h = res = size
	display = pygame.display.set_mode(res, RESIZABLE)
	updateDisplay()

def updateDisplay():
	display.fill(bg)

	y = (h - len(fields) * (label_height_total)) // 2
	mouse_pos_rect = (pygame.mouse.get_pos(), (1, 1))

	for i, field in enumerate(fields):
		rect = pygame.Rect((0, y + i*(label_height_total), w//2, label_height))
		if field is curr_field:
			state = SELECTED
		elif mouse_pos_rect in rect:
			state = HOVER
		else:
			state = NONE
		surf = field.render(state)
		display.blit(surf, (0, y + i*label_height_total))

	if mouse_pos_rect not in submit_button.get_rect():
		# if pygame.mouse.get_pressed(3): print(pygame.mouse.get_pressed())
		state = NONE
	elif pygame.mouse.get_pressed(3)[0]:
		state = SELECTED
	else:
		state = HOVER
	button_surf = submit_button.render(state)
	display.blit(button_surf, (submit_button.get_x(), submit_button.get_y()))

	outs_surf = render_outputs(inputs)
	x = w//2 + (w//2 - outs_surf.get_width())//2
	y = (h - outs_surf.get_height()) // 2
	display.blit(outs_surf, (x, y))

	# OUTPUT DIVIDER
	display.fill(divider_colour, (w//2, 75, 2, h-150))

	# updateStat(update = False)
	pygame.display.flip()

def toggleFullscreen():
	global pres, res, w, h, display
	res, pres =  pres, res
	w, h = res
	if display.get_flags()&FULLSCREEN: resize(res)
	else: display = pygame.display.set_mode(res, FULLSCREEN); updateDisplay()

class InputField:
	def __init__(self, label, data):
		self.label = label
		self.text = ''
		self.hint = ''
		self.data = data
	
	def render(self, state):
		surf_width = w//5 + padding + box_width

		if   state is SELECTED: col = selected_box_colour
		elif state is HOVER: col = hover_box_colour
		else: col = box_colour

		lsurf = font.render(self.label, True, fg)
		out = pygame.Surface((surf_width, label_height), SRCALPHA)
		tx = surf_width-padding - box_width - lsurf.get_width()
		out.blit(lsurf, (tx, 0))

		tx += lsurf.get_width() + padding
		out.fill(col, (tx, 0, box_width, label_height+1))

		if state is SELECTED:
			hsurf = font.render(self.hint, True, hint_colour)
			out.blit(hsurf, (tx+padding, 0))
		tsurf = font.render(self.text, True, fg)
		out.blit(tsurf, (tx+padding, 0))

		return out

class Button:
	def __init__(self, label, w, h):
		self.label = label
		self.w = w
		self.h = h

	def get_x(self):
		return NotImplemented

	def get_y(self):
		return NotImplemented

	def get_rect(self):
		return pygame.Rect(self.get_x(), self.get_y(), self.w, self.h)

	def render(self, state):
		out = pygame.Surface((self.w, self.h), SRCALPHA)  # alpha for if we do rounded

		if   state == HOVER: col = hover_button_colour
		elif state == SELECTED: col = selected_button_colour
		else: col = button_colour

		tsurf = bfont.render(self.label, True, fg)
		x = (self.w - tsurf.get_width()) // 2
		y = (self.h - tsurf.get_height()) // 2

		# TODO rounded
		out.fill(col)

		out.blit(tsurf, (x, y))
		return out

	def handler(self):
		return NotImplemented

class SubmitButton(Button):
	def handler(self):
		global outputs, inputs
		inputs = [field.text for field in fields]
		# send inputs to ML
		print('we did the thing')
		outputs = get_outputs(*inputs)

	def get_x(self):
		# return w//4 + padding
		return (w//2 - self.w)//2

	def get_y(self):
		y = (h - len(fields) * (label_height_total)) // 2
		return (y+label_height_total*(len(fields)+1))

def get_next_hint(curr_hint, pref, data):
	ready = not curr_hint
	for plid in data:
		if plid.startswith(pref):
			if ready: break
			if plid == curr_hint: ready = True
	else:
		if curr_hint: return get_next_hint('', pref, data)
		return ''

	if plid == curr_hint: return ''
	return plid

def get_outputs(plid, quarter, month):
	# talks to "backend"

	try:
		year = int(quarter[-4:])
		quarter = quarter[:2]
		month = (
			'JAN',
			'FEB',
			'MAR',
			'APR',
			'MAY',
			'JUN',
			'JUL',
			'AUG',
			'SEP',
			'OCT',
			'NOV',
			'DEC',
		).index(month[:3]) + 1
		return [
			str(backend.predict(plid, quarter, month, year))
		]
	except ValueError: return ['Invalid Input']

def render_outputs(inputs):
	global outputs

	out_height = label_height_total * max(len(outputs), 1)
	out = pygame.Surface((w//2, out_height), SRCALPHA)

	if not outputs:
		outputs.append('No predictions available yet.')

	for i, o in enumerate(outputs):
		tsurf = sfont.render(o, True, fg)
		out.blit(tsurf, ((w//2 - tsurf.get_width())//2, label_height_total*i))

	return out

fields = (

	# input labels and submit submit_button
	# INPUTS:
	# plid
	# fiscal quarter
	# fiscal month
	# booked quantity [OUT.]
	# booking date [OUT?]
	# business unit [IRR]
	# product family [IRR]

	InputField('PLID', data.plids),
	InputField('Fiscal Quarter', data.quarters),
	InputField('Fiscal Month', data.months),
)

submit_button = SubmitButton('Predict', 400, 100)

pos = [0, 0]
dragging = False
curr_field = None
curr_field_index = None

inputs = [field.text for field in fields]
outputs = []

resize(res)
pygame.key.set_repeat(500, 20)
pygame.display.set_caption('Poisson Pivots')
pres = pygame.display.list_modes()[0]
clock = pygame.time.Clock()
running = True
while running:
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if   event.key == K_F11: toggleFullscreen()
			# elif event.key == K_ESCAPE: running = False
			elif curr_field_index is None:
				if not fields: continue
				if event.key == K_TAB:
					curr_field_index = 0
					curr_field = fields[curr_field_index]
			elif pygame.key.get_mods() & (KMOD_LCTRL|KMOD_RCTRL):
				if event.key == K_BACKSPACE:
					split = curr_field.text.rsplit(maxsplit=1)
					if len(split) <= 1: curr_field.text = ''
					else: curr_field.text = split[0]
				elif event.key == K_v:
					... # paste
			elif event.key == K_ESCAPE:
				curr_field.hint = ''
				continue
			elif event.key == K_RETURN:
				if curr_field.hint:
					curr_field.text = curr_field.hint
					curr_field.hint = ''
					continue
			elif event.key == K_TAB:
				if curr_field.hint:
					curr_field.hint = get_next_hint(curr_field.hint, curr_field.text, curr_field.data)
					continue
				curr_field_index += 1
				if curr_field_index >= len(fields): curr_field_index = 0
				curr_field = fields[curr_field_index]
			elif event.key == K_BACKSPACE:
				curr_field.text = curr_field.text[:-1]
			elif event.unicode and event.unicode.isprintable():
				curr_field.text += event.unicode
			else:
				continue

			if curr_field is not None:
				# if curr_field_index_field.text:
					curr_field.hint = get_next_hint('', curr_field.text, curr_field.data)
				# else:
				# 	curr_field.hint = ''

		elif event.type == VIDEORESIZE:
			if not display.get_flags()&FULLSCREEN: resize(event.size)
		elif event.type == QUIT: running = False
		elif event.type == MOUSEBUTTONDOWN:
			if event.button in (4, 5):
				delta = event.button*2-9
			elif event.button == 1:
				x, y = event.pos
				if x > w//2: curr_field = None; curr_field_index = None; continue

				fields_start = (h - len(fields) * (label_height_total)) // 2
				y -= fields_start

				if y%label_height_total > label_height: curr_field = None; curr_field_index = None; continue
				curr_field_index = y // label_height_total
				if curr_field_index >= len(fields):
					if (event.pos, (1,  1)) in submit_button.get_rect():
						submit_button.handler()
					curr_field = None; curr_field_index = None; continue
				if curr_field_index < 0: curr_field = None; curr_field_index = None; continue
				curr_field = fields[curr_field_index]
				# print(curr_field.label)

		elif event.type == MOUSEBUTTONUP:
			if event.button == 1:
				dragging = False
		# elif event.type == MOUSEMOTION:
		# 	if dragging:
		# 		pos[0] += event.rel[0]
		# 		pos[1] += event.rel[1]

	updateDisplay()
	# updateStat()
	clock.tick(fps)