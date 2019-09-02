# coding: utf-8

# https://gist.github.com/Phuket2/1430ac7f8eba11fdaff5

# https://forum.omz-software.com/topic/2953/calendar-view-class/2

import calendar
import datetime as dt
import ui
from console import clear
import json
from random import randint as ran
from scripter import *

# reverse comment to initialize data file
# !!! Save data as not reversible !!!
INIT = False
#INIT = True

class CalendarView(ui.View):

	def __init__(self,fldname,dateval,action=None, grid=[],*args, **kwargs):
		ui.View.__init__(self, *args, **kwargs) # here
	
		self.firstweekday=0		
		self.d_clr_none=1.0, 1.0, 1.0, 1.0
		self.d_clr_bank=1.0, .0, .0, 1.0
		self.d_clr_off=1.0, .64, .16, 1.0
		self.bank_total = 0
		self.banked_hours = 0
		self.enter_offshore = False
		self.offshore_hours = 0
		self.offshore_start=dt.datetime.today()
		self.offshore_end=dt.datetime.today()
		calendar.setfirstweekday(calendar.SUNDAY)
		self.grid=grid
		self.sum_bank_hours()
		self.banked_hours=int(self.grid[0][0])
		self.days = calendar.weekheader(3).split()
		self.width,self.height = ui.get_screen_size() #here
		cv = ui.View(name=fldname)
		cv.frame = (0,95,self.width,255)
		cv.background_color = 'yellow'
		cv.border_color = 'yellow'
		cv.border_width = 2
		
		# application buttons
		self.view = cv
		self.action = action
		prv_mth = ui.Button(title='<')
		prv_mth.frame = (5,5,50,25)
		prv_mth.action = self.prev_pressed
		self.day_color = prv_mth.tint_color
		self.view.add_subview(prv_mth)
		nxt_mth = ui.Button(title='>')
		nxt_mth.frame = (56,5,50,25)
		nxt_mth.action = self.next_pressed
		self.view.add_subview(nxt_mth)
		
		label = ui.Label(name='caltitle')
		self.caldate = dateval #dt.datetime.strptime(dateval,'%d/%m/%Y')
		self.curdate = dt.datetime.today()
		label.text = str(self.caldate.strftime('%B  %Y'))
		label.frame = (107,5,200,25)
		label.alignment = ui.ALIGN_CENTER
		self.view.add_subview(label)
		
		# paystub Banked hours	
		banked_label = ui.Label(name='bankedtitle',text='Bank Hr Paystub:',frame=(5,8*31,150,30))
		self.view.add_subview(banked_label)
		
		banked_value = ui.TextField(name='bankedval',text=str(self.banked_hours),frame=(155,8*31,100,30), enabled = True, keyboard_type=ui.KEYBOARD_NUMBERS,action=self.banked_val_changed)
		self.view.add_subview(banked_value)
		
		# future banked (offshore) hours
		offshore_label = ui.Label(name='offshoretitle',text='Future Bank Hr:',frame=(5,9*31,150,30))
		self.view.add_subview(offshore_label)
		
		offshore_value = ui.TextField(name='offshoreval',text=str(self.offshore_hours),frame=(155,9*31,100,30), enabled = False, keyboard_type=ui.KEYBOARD_NUMBERS)
		self.view.add_subview(offshore_value)		
		
		# Bank hours used
		bank_label = ui.Label(name='banktitle',text='Bank Hr Use:',frame=(5,10*31,150,30))
		self.view.add_subview(bank_label)
		
		bank_value = ui.TextField(name='bankval',text=str(self.bank_total),frame=(155,10*31,100,30), enabled = False)
		self.view.add_subview(bank_value)
		
		#remaining bank hours
		bank_remain_label = ui.Label(name='remaintitle',text='Bank Hr Remain:',frame=(5,11*31,150,30))
		self.view.add_subview(bank_remain_label)
		# todo: add a date relative bank remaining field
		bank_remain_value = ui.TextField(name='remainval',text=str(self.banked_hours + self.offshore_hours -self.bank_total),frame=(155,11*31,100,30), enabled = False)
		self.view.add_subview(bank_remain_value)
		
		# Offshore Hour entry
		offshore_entry_label = ui.Label(name='offshoretitle',text='Enter Offshore Days:',frame=(5,12*31,200,30))
		self.view.add_subview(offshore_entry_label)
		
		offshore_switch = ui.Switch(title='y ', frame=(190,12*31,200,30), action = self.offshore_switch)
		
		self.view.add_subview(offshore_switch)
		'''		
		offshore_entry_start_value = ui.DatePicker(name='offshore_start',frame=(15,12*31,250,60), mode=ui.DATE_PICKER_MODE_DATE,background_color=(.94, 1.0, .87), action=self.offshore_start_action)
		self.view.add_subview(offshore_entry_start_value)
		
		offshore_entry_end_value = ui.DatePicker(name='offshore_end',frame=(15,14*31,250,60), mode=ui.DATE_PICKER_MODE_DATE,background_color=(.94, 1.0, .87), action=self.offshore_end_action)
		self.view.add_subview(offshore_entry_end_value)		
		
		offshore_btn = ui.Button(title=' Add to Cal ', frame=(280,14.5*31,200,30), action = self.add_offshore, font=('Arial Rounded MT Bold',15),border_color='black', border_width=2,alignment=ui.ALIGN_CENTER)
		
		self.view.add_subview(offshore_btn)
		'''
		today_btn = ui.Button(title='Today')
		today_btn.frame = (self.width-60,5,50,25)
		today_btn.action = self.today_pressed
		self.view.add_subview(today_btn)

		self.firstdate = dt.date(self.caldate.year,self.caldate.month,1)
		self.create_buttons()
		self.draw_calendar()
		
	def offshore_switch(self,sender):
		self.enter_offshore=sender.value
#		print('enable:',self.enter_offshore)
		
	def offshore_start_action(self,sender):
		self.offshore_start = self.view['offshore_start'].date

	def offshore_end_action(self,sender):
		self.offshore_end = self.view['offshore_end'].date

	def add_offshore(self,sender):
		offshore_start_m = self.offshore_start.month
		offshore_start_d = self.offshore_start.day
		
		offshore_end_m = self.offshore_end.month
		offshore_end_d = self.offshore_end.day
#		print('output',offshore_start_d,offshore_start_m)
		# Need firstdate of offshore start month
		start_firstdate = dt.date(self.caldate.year,offshore_start_m,1)
#		print('1date',start_firstdate)
		start_firstweekday = start_firstdate.weekday()
		num_offshore_days= (self.offshore_end- self.offshore_start).days
		print(num_offshore_days)
		print(list(range(0,num_offshore_days)))
#		print('strt_f_wkdy1',start_firstweekday,)		
		start_firstweekday = (start_firstweekday + 1) % 7		
		# fill in grid
		for day in range(num_offshore_days):
			self.grid[offshore_start_m][ 7+start_firstweekday+offshore_start_d-1 + day+1] = 2
#		print('strt_f_wkdy2',start_firstweekday,)
	def save_data(self):
		try:
#			print('saving....')
			with open('Calview2.data', 'w') as f:
				json.dump(self.grid,f)		
		except EOFError:
			pass
	
	def banked_val_changed(self,sender):
#		print(self.view['bankedval'].text)
		self.grid[0][0] = self.banked_hours=int(self.view['bankedval'].text)
		self.view['remainval'].text=str(self.banked_hours-self.bank_total)
		self.save_data()
		
	def sum_bank_hours(self):
		for row in range(1,13):
			for col in range(49):
				if self.grid[row][col] == 1:
					self.bank_total+=8
				elif self.grid[row][col] ==2:
					self.offshore_hours+=8
		
	def create_buttons(self):
		''' Create 7x7 grid (calendar) with no numbers in boxes. draw_calendar() inserts numbers
		'''
		y = 0
		for i in range(49):
			daytitle = self.days[i] if i<7 else ''
			button = ui.Button(name='day'+str(i),title=daytitle)
			if i>=7:
				button.action = self.button_pressed
				y = 1
			if i >= 14: y = 2
			if i >= 21: y = 3
			if i >= 28: y = 4				
			if i >= 35: y = 5
			if i >= 42: y = 6
			button.frame = (5+(i%7)*51,(31+(y*31)),50,30)
			button.border_color = '#dadada'
			button.border_width = 1
			button.background_color = 'white' if i%7 else '#fff5f5'
			self.view.add_subview(button)

	def draw_calendar(self):
		''' insert number into calendar depending on month chosen. color accordingly from data file. 
		'''
		self.lastdate = self.last_day_of_month(self.firstdate)
		self.firstweekday = self.firstdate.weekday()
		self.firstweekday = (self.firstweekday + 1) % 7
		last_day = self.lastdate.day
		self.view['caltitle'].text = str(self.firstdate.strftime('%B  %Y'))
		for i in range(7,49):
			dy = i-6-self.firstweekday
			if (self.firstweekday+7<=i) and dy<=last_day:
				strtitle = str(dy)
			else:
				strtitle = ''
			self.view['day'+str(i)].title = strtitle
			# Decide color from grid.data
			color=int(self.grid[self.firstdate.month][i])
			if color== 0: d_color = self.d_clr_none
			if color== 1: d_color = self.d_clr_bank	
			if color== 2: d_color = self.d_clr_off
			self.view['day'+str(i)].background_color = d_color
			
			# Hilight today if it is this Month
			if (self.firstdate.year == self.curdate.year) and (self.firstdate.month == self.curdate.month) and (self.curdate.day == dy):
				self.view['day'+str(i)].tint_color = 'green'
			# Hilight last pressed date. keep?
			elif (self.firstdate.year == self.caldate.year) and (self.firstdate.month == self.caldate.month) and (self.caldate.day == dy):
				self.view['day'+str(i)].tint_color = 'black'
#				print('black')
			else:
				self.view['day'+str(i)].tint_color =  self.day_color

	def button_pressed(self,sender):
		''' A calendar date pressed = a banked hour to be used. color accordingly and process calculations
		'''
		if (self.enter_offshore == True and sender.background_color != self.d_clr_off):
			sender.background_color = self.d_clr_off
			new_color_num = 2		
			self.offshore_hours+=8
			rotate(sender, 360, duration=0.5, ease_func=linear)
		elif 	(sender.background_color == self.d_clr_none or sender.background_color == self.d_clr_off and self.enter_offshore != True):
			sender.background_color = self.d_clr_bank
			self.bank_total+=8.0
			new_color_num=1
			rotate(sender, 360, duration=0.5, ease_func=linear)
		else: 	
			sender.background_color = 'white'
			if (self.enter_offshore == False):
				self.bank_total-=8.0
			if (self.enter_offshore == True):
				self.offshore_hours-=8
			new_color_num=0
			rotate(sender, 360, duration=0.5, ease_func=linear)
		self.caldate = dt.date(self.firstdate.year,self.firstdate.month,int(sender.title))
		# update local data
		self.grid[self.firstdate.month][7+self.firstweekday+ int(sender.title)-1] = new_color_num
		self.grid[0][0]=self.banked_hours
		# Math calculations
#		self.banked_hours = float(self.view['bankedval'].text)
		self.view['bankval'].text= str(self.bank_total)
		self.view['remainval'].text= str(self.banked_hours+self.offshore_hours-self.bank_total)
		self.view['bankedval'].text= str(self.banked_hours)
		self.view['offshoreval'].text= str(self.offshore_hours)
		
		if self.action:
			(self.action)(self)
		# redundant if close save eventually works!	
		self.save_data()

	def prev_pressed(self,sender):
		if self.firstdate.month == 1:
			self.firstdate = dt.date(self.firstdate.year-1,12,1)
		else:
			self.firstdate = dt.date(self.firstdate.year,self.firstdate.month-1,1)
		self.draw_calendar()

	def next_pressed(self,sender):
		if self.firstdate.month == 12:
			self.firstdate = dt.date(self.firstdate.year+1,1,1)
		else:
			self.firstdate = dt.date(self.firstdate.year,self.firstdate.month+1,1)
		self.draw_calendar()

	def today_pressed(self,sender):
		self.firstdate = dt.date(self.curdate.year,self.curdate.month,1)
		self.draw_calendar()

	def last_day_of_month(self,date):
		if date.month == 12:
			return date.replace(day=31)
		return date.replace(month=date.month+1, day=1) - dt.timedelta(days=1)
		
	def will_close(self):
#		print('close')
		try:
			print('closing....')
			with open('Calview2.data', 'w') as f:
				json.dump(self.grid,f)		
		except EOFError:
			print('close error')
			pass
			
#	def done_button(self,sender):
#		print('done')
#		self.save_data()
def calendar_action(sender):
#	print(sender.caldate)
	pass
	
#	sender.view.close()

if __name__ == '__main__':
	clear()
	try:
		if (INIT):
			with open('Calview2.data', 'w') as f:
				grid = [[0 for col in range(49)] for row in range(12)] 	
				grid = [['0.0',(str(dt.datetime.today()))],]+grid
				json.dump(grid,f)		
		else:
			with open('Calview2.data', 'r') as f:
				grid = json.load(f)			
			# loaded files are sub-scriptable
#			print(grid[4][3])
	except EOFError:
		grid = [[0 for col in xrange(49)] for row in xrange(12)] 	
		grid = [['0.0',(str(dt.datetime.today()))],]+grid
#		print(grid)
	vw = CalendarView('Calendar',dt.datetime.today(),calendar_action, grid, frame = (0,0, 600, 800))
	vw.view.present('sheet')
