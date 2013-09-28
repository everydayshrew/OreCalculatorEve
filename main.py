import wx
import sys
import math
import time
import wx.grid as gridlib
from wx.lib.mixins.listctrl import ColumnSorterMixin
from fetchdata import fetchData
from fetchdata import fetchDate



########################################################################
# For some odd reason, SortedListCtrl won't be able sort if it doesn't have
# Sample data beforehand.  So I just stuck some values.  
output = {1: ('Pyroxeres', 183.63, 222.59, '0', '0', '0'), 2: ('Kernite', 187.02, 210.63, '0', '0', '0'), 3: ('Veldspar', 161.2, 159.46, '0', '0', '0'), 4: ('Plagioclase', 159.74, 190.96, '0', '0', '0'), 5: ('Hemorphite', 544.28, 306.4, '0', '0', '0'), 6: ('Spodumain', 373.27, 217.27, '0', '0', '0'), 7: ('Crokite', 252.1, 301.74, '0', '0', '0'), 8: ('Arkonor', 241.69, 348.98, '0', '0', '0'), 9: ('Gneiss', 301.02, 252.84, '0', '0', '0'), 10: ('Jaspet', 223.81, 276.76, '0', '0', '0'), 11: ('Hedbergite', 266.84, 390.96, '0', '0', '0'), 12: ('Dark Ochre', 1534.01, 270.89, '0', '0', '0'), 13: ('Scordite', 182.6, 197.74, '0', '0', '0'), 14: ('Bistot', 249.75, 254.24, '0', '0', '0'), 15: ('Omber', 165.12, 159.86, '0', '0', '0'), 16: ('Mercoxit', 540.87, 493.66, '0', '0', '0')}

class SortedListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT, size=(580,-1))
        ColumnSorterMixin.__init__(self, len(output))
        self.itemDataMap = output

    def GetListCtrl(self):
        return self
 
########################################################################
class PanelOne(wx.Panel):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)

        # Status Box
        self.Bind(wx.EVT_ENTER_WINDOW, self.WidgetExit)
       
        ## Flavor Boxes
        wx.StaticBox(self, label='Mining Style', pos=(10,5), size=(330,220))
        wx.StaticBox(self, label='Advanced Options', pos=(350,5), size=(270,220))
        wx.StaticBox(self, label='Results', pos=(10, 235), size=(610,320))

        # Images: Mining Style Box
        wx.StaticBitmap(self, bitmap=wx.Image('icons/laser.png').ConvertToBitmap(),
                        pos=(65,45))
        wx.StaticBitmap(self, bitmap=wx.Image('icons/strip_1.png').ConvertToBitmap(),
                        pos=(215,45))

        # Core: Mining Style Box
        self.L_mining_btn = wx.RadioButton(self, pos=(55,35))
        self.L_strip_btn = wx.RadioButton(self, pos=(205,35))
        self.L_mining_st1 = wx.StaticText(self, label='Count:', pos=(85,115))
        self.L_mining_laseramount = wx.ComboBox(self, pos=(125, 110),
                                                choices=['1','2','3','4','5','6','7','8'],
                                                style=wx.CB_READONLY, value='1')
        self.L_strip_st1 = wx.StaticText(self, label='Count:', pos=(225, 115))
        self.L_strip_laseramount = wx.ComboBox(self, pos=(265, 110),
                                               choices=['1','2','3'],
                                               style=wx.CB_READONLY, value='1')
        self.yield_st1 = wx.StaticText(self, label='Yield (per laser):', pos=(60,160))
        self.yieldamount = wx.TextCtrl(self, size=(100,-1), pos=(145, 155),
                                       style=wx.TE_RIGHT, value='0')
        self.yield_st2 = wx.StaticText(self, label='m^3', pos=(250, 160))
        self.calculate_btn = wx.Button(self, label='Calculate', pos=(135,190))

        # Core Hiding: Mining Style Box
        self.L_strip_st1.Hide()
        self.L_strip_laseramount.Hide()
        self.L_mining_st1.Hide()
        self.L_mining_laseramount.Hide()

        # Button Bindings: Mining Style Box
        self.L_mining_btn.Bind(wx.EVT_RADIOBUTTON, self.hideStripInfo)
        self.L_strip_btn.Bind(wx.EVT_RADIOBUTTON, self.hideMiningInfo)
        self.calculate_btn.Bind(wx.EVT_BUTTON, self.calcVals)
        self.calculate_btn.Bind(wx.EVT_ENTER_WINDOW,
                               lambda evt: self.OnWidgetEnter(evt, "Calculate Values"))
        self.calculate_btn.Bind(wx.EVT_LEAVE_WINDOW, self.WidgetExit)
  
        # Core: Advanced Options
        self.ferry_cb = wx.CheckBox(self, label='Cargohold Mining (Ferrying)',
                                       pos=(360, 40))
        self.ferry_time = wx.TextCtrl(self, size=(50,-1), pos=(510,60),
                                     value='180', style=wx.TE_RIGHT)
        self.ferry_st1 = wx.StaticText(self, label='seconds', pos=(565,65))
        self.ferry_st2 = wx.StaticText(self, label='Average time per trip:', pos=(390,65))
        self.ferry_st3 = wx.StaticText(self, label='Cargo Size:', pos=(390,95))
        self.ferry_cargo = wx.TextCtrl(self, size=(75,-1), pos=(485,90),
                                       value='1000')
        self.ferry_st4 = wx.StaticText(self, label='m^3', pos=(565,95))
        self.orca_cb = wx.CheckBox(self, label='Recieving Orca Bonuses', pos=(360, 150))
        self.orca_time = wx.TextCtrl(self, size=(50,-1), pos=(510,170),
                                     value='60')
        self.orca_st1 = wx.StaticText(self, label='Mining Cycle Time:', pos=(390,175))
        self.orca_st2 = wx.StaticText(self, label='seconds', pos=(565,175))

        # Core Hiding: Advanced Options Box
        self.ferry_time.Hide()
        self.ferry_st1.Hide()
        self.ferry_st2.Hide()
        self.ferry_st3.Hide()
        self.ferry_st4.Hide()
        self.ferry_cargo.Hide()

        self.orca_st1.Hide()
        self.orca_st2.Hide()
        self.orca_time.Hide()

        # Button Bindings: Advanced Options
        self.ferry_cb.Bind(wx.EVT_CHECKBOX, self.toggleCargoMining)
        self.orca_cb.Bind(wx.EVT_CHECKBOX, self.toggleOrcaBonuses)
        self.ferry_cb.Bind(wx.EVT_ENTER_WINDOW,
                               lambda evt: self.OnWidgetEnter(evt, "Check this if you're returning to a station after cargohold is filled"))
        self.orca_cb.Bind(wx.EVT_ENTER_WINDOW,
                               lambda evt: self.OnWidgetEnter(evt, "Check this if you're in a fleet with an orca."))
        self.ferry_cb.Bind(wx.EVT_LEAVE_WINDOW, self.WidgetExit)
        self.orca_cb.Bind(wx.EVT_LEAVE_WINDOW, self.WidgetExit)

        # Core: Results
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox.Add((-1,260))
        self.hbox.Add((25,285))
        self.dataOutput = SortedListCtrl(self)
        self.dataOutput.InsertColumn(0, 'Asteroid Name', wx.LIST_FORMAT_RIGHT, width=100)
        self.dataOutput.InsertColumn(1, 'Raw Value', wx.LIST_FORMAT_RIGHT, width=95)
        self.dataOutput.InsertColumn(2, 'Refined Value',wx.LIST_FORMAT_RIGHT, width=95)
        self.dataOutput.InsertColumn(3, 'Isk/s', wx.LIST_FORMAT_RIGHT, width=85)
        self.dataOutput.InsertColumn(4, 'Isk/hr', wx.LIST_FORMAT_RIGHT, width=106)
        self.dataOutput.InsertColumn(5, 'Efficency', wx.LIST_FORMAT_RIGHT, width=75)
        self.hbox.Add(self.dataOutput,0,wx.EXPAND)
        self.vbox.Add(self.hbox, 0)
        self.SetSizer(self.vbox, 0)

        self.Show(True)

    def hideStripInfo(self, e):
        self.L_strip_st1.Hide()
        self.L_strip_laseramount.Hide()
        self.L_mining_st1.Show()
        self.L_mining_laseramount.Show()

    def hideMiningInfo(self, e):
        self.L_strip_st1.Show()
        self.L_strip_laseramount.Show()
        self.L_mining_st1.Hide()
        self.L_mining_laseramount.Hide()

    def toggleCargoMining(self, e):
        if self.ferry_cb.GetValue():
            self.ferry_time.Show()
            self.ferry_st1.Show()
            self.ferry_st2.Show()
            self.ferry_st3.Show()
            self.ferry_st4.Show()
            self.ferry_cargo.Show()
        else:
            self.ferry_time.Hide()
            self.ferry_st1.Hide()
            self.ferry_st2.Hide()
            self.ferry_st3.Hide()
            self.ferry_st4.Hide()
            self.ferry_cargo.Hide()

    def toggleOrcaBonuses(self, e):
        if self.orca_cb.GetValue():
            self.orca_st1.Show()
            self.orca_st2.Show()
            self.orca_time.Show()
        else:
            self.orca_st1.Hide()
            self.orca_st2.Hide()
            self.orca_time.Hide()

    def calcVals(self, e):
         valid = True
         time = 0
         ptime = 0
         
         data = self.GetParent().queryOptions(self, "Ore")
         #print data
         if self.ferry_cb.GetValue():
            try:
                ftime = float(self.ferry_time.GetValue())
                cargo = float(self.ferry_cargo.GetValue())
            except ValueError:
                valid = False
         else:
            ftime = 0.0
            cargo = 1.0

         if self.orca_cb.GetValue():
            try:
                time = float(self.orca_time.GetValue())
                if self.L_mining_btn.GetValue():
                    ptime = 60.0
                else:
                    ptime = 180.0
            except ValueError:
                valid = False
         else:
            if self.L_mining_btn.GetValue():
                time = 60.0
                ptime = 60.0
            else:
                time = 180.0
                ptime = 180.0
         try:
             if self.L_mining_btn.GetValue():
                yieldamt = float(self.yieldamount.GetValue()) * float(self.L_mining_laseramount.GetValue())
             else:
                yieldamt = float(self.yieldamount.GetValue()) * float(self.L_strip_laseramount.GetValue())
         except ValueError:
             valid = False

         if yieldamt<=0: valid = False

         if valid:  
             rate = round(cargo / (((cargo/yieldamt)*time) + ftime),2)
             prate = round((yieldamt / ptime),2)

             i = 1
             output = {}
             for key in data:
                isk = round(rate*data[key][2],2)
                output[i] = (data[key][0], '{0:.2f}'.format(data[key][1]), '{0:.2f}'.format(data[key][2]), '{0:,.2f}'.format(isk),
                            '{0:,.2f}'.format(3600*isk), '{0:.2f}%'.format(rate/prate * 100))
                i += 1

             ## Clear list data
             self.dataOutput.DeleteAllItems()

             ## Write new data
             items = output.items()
             for key, ext in items:
                 index = self.dataOutput.InsertStringItem(sys.maxint, ext[0])
                 self.dataOutput.SetStringItem(index, 1, str(ext[1]))
                 self.dataOutput.SetStringItem(index, 2, str(ext[2]))
                 self.dataOutput.SetStringItem(index, 3, str(ext[3]))
                 self.dataOutput.SetStringItem(index, 4, str(ext[4]))
                 self.dataOutput.SetStringItem(index, 5, str(ext[5]))
                 self.dataOutput.SetItemData(index, key)
         else:
             self.warning()
             
    def OnWidgetEnter(self, e, string):
        self.GetParent().sb.SetStatusText(string)
        e.Skip()

    def WidgetExit(self, e):
        self.GetParent().sb.SetStatusText(self.GetParent().date \
                    + "\t                                                                                                                                                                    Region: " +
                    self.GetParent().fetch_region_name())
        #self.GetParent().settings_save()
        e.Skip()

    def warning(self):
        warn = wx.MessageDialog(None, 'You have invalid values!', 'Stop trying to break things!', wx.OK)
        ret = warn.ShowModal()

        if ret == wx.ID_OK:
            warn.Destroy()
        
         
 
########################################################################
class PanelTwo(wx.Panel):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)

        # Status Box
        self.Bind(wx.EVT_ENTER_WINDOW, self.WidgetExit)

        ## Flavor Boxes
        wx.StaticBox(self, label='Mining Style', pos=(10,5), size=(330,220))
        wx.StaticBox(self, label='Advanced Options', pos=(350,5), size=(270,220))
        wx.StaticBox(self, label='Results', pos=(10, 235), size=(610,320))

        # Images: Mining Style Box
        wx.StaticBitmap(self, bitmap=wx.Image('icons/strip_2.png').ConvertToBitmap(),
                        pos=(135,45))

        # Core: Mining Style Box
        #self.L_strip_btn = wx.RadioButton(self, pos=(130,35))
        self.L_strip_st1 = wx.StaticText(self, label='Count:', pos=(120, 115))
        self.L_strip_laseramount = wx.ComboBox(self, pos=(165, 110),
                                               choices=['1','2','3'],
                                               style=wx.CB_READONLY, value='1')
        self.yield_st1 = wx.StaticText(self, label='Mining time:', pos=(70,160))
        self.time = wx.TextCtrl(self, size=(60,-1), pos=(150, 155),
                                       style=wx.TE_RIGHT, value='500')
        self.yield_st2 = wx.StaticText(self, label='seconds', pos=(215, 160))
        self.calculate_btn = wx.Button(self, label='Calculate', pos=(135,190))

        # Core Hiding: Mining Style Box


        # Button Bindings: Mining Style Box
        self.calculate_btn.Bind(wx.EVT_BUTTON, self.calcVals)
        self.calculate_btn.Bind(wx.EVT_ENTER_WINDOW,
                               lambda evt: self.OnWidgetEnter(evt, "Calculate Values"))
        self.calculate_btn.Bind(wx.EVT_LEAVE_WINDOW, self.WidgetExit)
        
        # Core: Advanced Options
        self.ferry_cb = wx.CheckBox(self, label='Cargohold Mining (Ferrying)',
                                       pos=(360, 40))
        self.ferry_time = wx.TextCtrl(self, size=(50,-1), pos=(510,60),
                                     value='180', style=wx.TE_RIGHT)
        self.ferry_st1 = wx.StaticText(self, label='seconds', pos=(565,65))
        self.ferry_st2 = wx.StaticText(self, label='Average time per trip:', pos=(390,65))
        self.ferry_st3 = wx.StaticText(self, label='Cargo Size:', pos=(390,95))
        self.ferry_cargo = wx.TextCtrl(self, size=(75,-1), pos=(485,90),
                                       value='1000')
        self.ferry_st4 = wx.StaticText(self, label='m^3', pos=(565,95))

        # Core Hiding: Advanced Options Box
        self.ferry_time.Hide()
        self.ferry_st1.Hide()
        self.ferry_st2.Hide()
        self.ferry_st3.Hide()
        self.ferry_st4.Hide()
        self.ferry_cargo.Hide()

        # Button Bindings: Advanced Options
        self.ferry_cb.Bind(wx.EVT_CHECKBOX, self.toggleCargoMining)
        self.ferry_cb.Bind(wx.EVT_ENTER_WINDOW,
                               lambda evt: self.OnWidgetEnter(evt, "Check this if you're returning to a station after cargohold is filled"))
        self.ferry_cb.Bind(wx.EVT_LEAVE_WINDOW, self.WidgetExit)
       

        # Core: Results
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox.Add((-1,260))
        self.hbox.Add((25,285))
        self.dataOutput = SortedListCtrl(self)
        self.dataOutput.InsertColumn(0, 'Asteroid Name', wx.LIST_FORMAT_RIGHT, width=100)
        self.dataOutput.InsertColumn(1, 'Raw Value', wx.LIST_FORMAT_RIGHT, width=95)
        self.dataOutput.InsertColumn(2, 'Refined Value',wx.LIST_FORMAT_RIGHT, width=95)
        self.dataOutput.InsertColumn(3, 'Isk/s', wx.LIST_FORMAT_RIGHT, width=85)
        self.dataOutput.InsertColumn(4, 'Isk/hr', wx.LIST_FORMAT_RIGHT, width=106)
        self.dataOutput.InsertColumn(5, 'Efficency', wx.LIST_FORMAT_RIGHT, width=75)
        self.hbox.Add(self.dataOutput,0,wx.EXPAND)
        self.vbox.Add(self.hbox, 0)
        self.SetSizer(self.vbox, 0)

        self.Show(True)

    def toggleCargoMining(self, e):
        if self.ferry_cb.GetValue():
            self.ferry_time.Show()
            self.ferry_st1.Show()
            self.ferry_st2.Show()
            self.ferry_st3.Show()
            self.ferry_st4.Show()
            self.ferry_cargo.Show()
        else:
            self.ferry_time.Hide()
            self.ferry_st1.Hide()
            self.ferry_st2.Hide()
            self.ferry_st3.Hide()
            self.ferry_st4.Hide()
            self.ferry_cargo.Hide()

    def calcVals(self, e):

         valid = True
         time = 0
         
         
         data = self.GetParent().queryOptions(self, "Ice")
         #print data
         if self.ferry_cb.GetValue():
            try:
                ftime = float(self.ferry_time.GetValue())
                cargo = math.floor(float(self.ferry_cargo.GetValue())/1000)*1000
            except ValueError:
                valid = False
         else:
            ftime = 0.0
            cargo = 1

         try:
             yieldamt = float(self.L_strip_laseramount.GetValue()) * 1000
             time = round(float(self.time.GetValue()),2)
         except ValueError:
             valid = False

         if time <= 0: valid = False

         if valid:
             rate = round((cargo / (((cargo/yieldamt)*time) + ftime))/ 1000,5) 
             prate = round((yieldamt / 1000 / time),5)

             #print "cargo: {}, rate: {}, prate: {}".format(cargo, rate, prate)

             i = 1
             output = {}
             for key in data:
                isk = round(rate*data[key][2],2)
                output[i] = (data[key][0], '{0:,.2f}'.format(data[key][1]), '{0:,.2f}'.format(data[key][2]), '{0:,.2f}'.format(isk),
                            '{0:,.2f}'.format(3600*isk), '{0:.2f}%'.format(rate/prate * 100))
                i += 1

             ## Clear list data
             self.dataOutput.DeleteAllItems()

             ## Write new data
             items = output.items()
             for key, ext in items:
                 index = self.dataOutput.InsertStringItem(sys.maxint, ext[0])
                 self.dataOutput.SetStringItem(index, 1, str(ext[1]))
                 self.dataOutput.SetStringItem(index, 2, str(ext[2]))
                 self.dataOutput.SetStringItem(index, 3, str(ext[3]))
                 self.dataOutput.SetStringItem(index, 4, str(ext[4]))
                 self.dataOutput.SetStringItem(index, 5, str(ext[5]))
                 self.dataOutput.SetItemData(index, key)
         else:
             self.warning()

    def OnWidgetEnter(self, e, string):
        self.GetParent().sb.SetStatusText(string)
        e.Skip()

    def WidgetExit(self, e):
        self.GetParent().sb.SetStatusText(self.GetParent().date \
                    + "\t                                                                                                                                                                    Region: " +
                    self.GetParent().fetch_region_name())
        e.Skip()

    def warning(self):
        warn = wx.MessageDialog(None, 'You have invalid values!', 'Stop trying to break things!', wx.OK)
        ret = warn.ShowModal()

        if ret == wx.ID_OK:
            warn.Destroy()

########################################################################
class PanelThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        
        wx.StaticText(self, pos=(300,300), label='Coming Eventually')

########################################################################
class PanelFour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        
        Names = ("Tritanium", "Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", 
            "Megacyte", "Morphite", 'Veldspar','Scordite', 'Pyroxeres', 'Plagioclase',
            'Omber', 'Kernite', 'Jaspet', 'Hemorphite', 'Hedbergite', 'Gneiss',
            'Dark Ochre', 'Crokite', 'Spodumain', 'Bistot', 'Arkonor', 'Mercoxit',
            "Helium Isotopes", "Oxygen Isotopes", "Nitrogen Isotopes", "Hydrogen Isotopes",
            "Liquid Ozone", "Heavy Water", "Strontium Clathrates", "Dark Glitter",
            "Glacial Mass", "Glare Crust", "White Glaze", "Blue Ice", "Clear Icicle",
            "Gelidus", "Krystallos")

        dataFile = open("customvals.txt", "r")
        vals = dataFile.readline()
        dataFile.close()
        vals = vals.replace("[","")
        vals = vals.replace("]","")
        pvals = vals.split(",")
        
        y = 20
        self.boxes = []
        for self.i in range(0,len(Names)):
            x = (self.i%3)*200 + 20
            if self.i > 0 and self.i%3 == 0:
                y += 45
                
            temp = wx.StaticBitmap(self,
                        bitmap=wx.Image('icons/'+Names[self.i]+'.png').Rescale(32,32).ConvertToBitmap(),
                        pos=(x,y))
            wx.StaticText(self, pos=(x+35,y-5), label=str(Names[self.i]))
            self.boxes.append(wx.TextCtrl(self, size=(75,-1), pos=(x+45, y+10),
                                             value=str(pvals[1+3*self.i])))

        self.set_btn = wx.Button(self, label='Save', pos=(550,570))
        self.res_btn = wx.Button(self, label='Restore\nDefaults', size=(75,45),
                                 pos=(550,515))

        self.set_btn.Bind(wx.EVT_BUTTON, self.setVals)
        self.res_btn.Bind(wx.EVT_BUTTON, self.resVals)
        self.WidgetExit

    def setVals(self, e):
        temp = []
        valid = True
        
        for n in range(0,len(self.boxes)):
            try:
                value = float(self.boxes[n].GetValue())
                temp.append(0) # Blank for future expansion
                temp.append(value)
                temp.append(0) # Blank for future expansion
            except ValueError:
                valid = False

        if valid:
            dataFile = open("customvals.txt", "w")
            vals = dataFile.writelines(str(temp))
            dataFile.close()
        else:
            self.warning

    def resVals(self, e):
        temp = []
        dataFile = open("pulledvals.dat", "r")
        temp = dataFile.readline()
        temp = dataFile.readline()
        dataFile.close()
        temp = temp.replace("[","")
        temp = temp.replace("]","")
        old = temp.split(",")
        temp = []
        for n in range(0,len(self.boxes)):
            self.boxes[n].SetValue(str(old[1+n*3]))
            temp.append(0)
            temp.append(float(self.boxes[n].GetValue()))
            temp.append(0)

        dataFile = open("customvals.txt", "w")
        vals = dataFile.writelines(str(temp))
        dataFile.close()
        self.Refresh()
            
    def OnWidgetEnter(self, e, string):
        self.GetParent().sb.SetStatusText(string)
        e.Skip()

    def WidgetExit(self, e):
        self.GetParent().sb.SetStatusText(self.GetParent().date \
                    + "\t                                                                                                                                                                    Region: " +
                    self.GetParent().fetch_region_name())
        e.Skip()

    def warning(self):
        warn = wx.MessageDialog(None, 'You have invalid values!', 'Stop trying to break things!', wx.OK)
        ret = warn.ShowModal()

        if ret == wx.ID_OK:
            warn.Destroy()       
        

########################################################################
class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 
                          "Obscenely Elaborate Yield Calculator", size=(650,725))

        self.sb = self.CreateStatusBar()
        temp = fetchDate()
        self.date = "Last Market Data was Taken at: {}/{}/{} at {}:{}".format(temp[0],
                        temp[1],temp[2],temp[3],temp[4])
 
        self.panel_one = PanelOne(self)
        self.panel_two = PanelTwo(self)
        self.panel_three = PanelThree(self)
        self.panel_four = PanelFour(self)
        self.panel_two.Hide()
        self.panel_three.Hide()
        self.panel_four.Hide()
 
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panel_one, 1, wx.EXPAND)
        self.sizer.Add(self.panel_two, 1, wx.EXPAND)
        self.sizer.Add(self.panel_three, 1, wx.EXPAND)
        self.sizer.Add(self.panel_four, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
 
 
        menubar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        
        '''modeMenu = wx.Menu()
        option_1 = modeMenu.Append(wx.ID_ANY, "Ore", "1")
        option_2 = modeMenu.Append(wx.ID_ANY, "Ice", "2")
        option_3 = modeMenu.Append(wx.ID_ANY, "Gas", "3")
        self.Bind(wx.EVT_MENU, lambda evt: self.onSwitchPanels(evt, 1), option_1)
        self.Bind(wx.EVT_MENU, lambda evt: self.onSwitchPanels(evt, 2), option_2)
        self.Bind(wx.EVT_MENU, lambda evt: self.onSwitchPanels(evt, 3), option_3)
        menubar.Append(modeMenu, '&Mode')'''

        marketMenu = wx.Menu()
        marketSubMenu = wx.Menu()
        market_submenu_2 = wx.Menu()
        option_update = marketMenu.Append(wx.ID_ANY, "Force Update Market Prices", "")
        self.Bind(wx.EVT_TOOL, lambda evt: self.Update(evt, ""), option_update)
        
        self.rss = marketSubMenu.Append(wx.ID_ANY, "Sell Ore for Maximized Profits",
                                       '', kind=wx.ITEM_RADIO)
        self.rfs = marketSubMenu.Append(wx.ID_ANY, "Sell Ore for Quickest Selling",
                                       '', kind=wx.ITEM_RADIO)
        marketSubMenu.AppendSeparator()
        self.ss = marketSubMenu.Append(wx.ID_ANY, "Sell Minerals for Maximized Profits",
                                       '', kind=wx.ITEM_RADIO)
        self.fs = marketSubMenu.Append(wx.ID_ANY, "Sell Minerals for Quickest Selling",
                                       '', kind=wx.ITEM_RADIO)
        marketSubMenu.AppendSeparator()
        self.cs = marketSubMenu.Append(wx.ID_ANY, "Use Custom Prices", '',
                                       kind=wx.ITEM_CHECK)
        marketMenu.AppendMenu(wx.ID_ANY, 'Selling Style', marketSubMenu)

        self.jita = market_submenu_2.Append(wx.ID_ANY, "Jita", '',
                                            kind=wx.ITEM_RADIO)
        self.hek = market_submenu_2.Append(wx.ID_ANY, "Hek", '',
                                            kind=wx.ITEM_RADIO)
        self.rens = market_submenu_2.Append(wx.ID_ANY, "Rens", '',
                                            kind=wx.ITEM_RADIO)
        self.dodixie = market_submenu_2.Append(wx.ID_ANY, "Dodixie", '',
                                            kind=wx.ITEM_RADIO)
        self.amarr = market_submenu_2.Append(wx.ID_ANY, "Amarr", '',
                                            kind=wx.ITEM_RADIO)
        marketMenu.AppendMenu(wx.ID_ANY, 'Region', market_submenu_2)

        self.Bind(wx.EVT_TOOL, lambda evt: self.Update(evt, "Jita"),
                  self.jita)
        self.Bind(wx.EVT_TOOL, lambda evt: self.Update(evt, "Hek"),
                  self.hek)
        self.Bind(wx.EVT_TOOL, lambda evt: self.Update(evt, "Rens"),
                  self.rens)
        self.Bind(wx.EVT_TOOL, lambda evt: self.Update(evt, "Dodixie"),
                  self.dodixie)
        self.Bind(wx.EVT_TOOL, lambda evt: self.Update(evt, "Amarr"),
                  self.amarr)
        
        
        
        option_set = marketMenu.Append(wx.ID_ANY, "Set Prices Manually", "")
        self.Bind(wx.EVT_TOOL, lambda evt: self.onSwitchPanels(evt, 4), option_set) 
        menubar.Append(marketMenu, '&Market')

        helpMenu = wx.Menu()
        #option_help = helpMenu.Append(wx.ID_HELP, "&Help")
        option_about = helpMenu.Append(wx.ID_ABOUT, "&About")
        self.Bind(wx.EVT_MENU, self.about, option_about)
        option_exit = helpMenu.Append(wx.ID_EXIT, "Exit")
        self.Bind(wx.EVT_MENU, self.OnQuit, option_exit)
        menubar.Append(helpMenu, '&Other')

        #--- Load Settings
        # Figure how to put this in its own function
        settings = self.settings_load()
        marketSubMenu.Check(self.rfs.GetId(), True if settings[0]=="True" else False)
        marketSubMenu.Check(self.rss.GetId(), True if settings[1]=="True" else False)
        marketSubMenu.Check(self.fs.GetId(), True if settings[2]=="True" else False)
        marketSubMenu.Check(self.ss.GetId(), True if settings[3]=="True" else False)
        marketSubMenu.Check(self.cs.GetId(), True if settings[4]=="True" else False)
        if settings[5] == "Hek": market_submenu_2.Check(self.hek.GetId(), True)
        elif settings[5] == "Rens": market_submenu_2.Check(self.rens.GetId(), True)
        elif settings[5] == "Dodixie": market_submenu_2.Check(self.dodixie.GetId(), True)
        elif settings[5] == "Amarr": market_submenu_2.Check(self.amarr.GetId(), True)
        else: market_submenu_2.Check(self.jita.GetId(), True)
        
        self.SetMenuBar(menubar)

        toolbar = self.CreateToolBar()
        ore_bar = toolbar.AddSimpleTool(wx.ID_ANY, wx.Image('icons/strip_1.png').Rescale(32,32).ConvertToBitmap(),
                                        'Ore Mining', 'Ore Mining')
        ice_bar = toolbar.AddSimpleTool(wx.ID_ANY, wx.Image('icons/strip_2.png').Rescale(32,32).ConvertToBitmap(),
                                        'Ice Mining', 'Ice Mining')
        gas_bar = toolbar.AddSimpleTool(wx.ID_ANY, wx.Image('icons/gas.png').Rescale(32,32).ConvertToBitmap(),
                                        'Gas Mining', 'Gas Mining')
        self.Bind(wx.EVT_TOOL, lambda evt: self.onSwitchPanels(evt, 1), ore_bar)
        self.Bind(wx.EVT_TOOL, lambda evt: self.onSwitchPanels(evt, 2), ice_bar)
        self.Bind(wx.EVT_TOOL, lambda evt: self.onSwitchPanels(evt, 3), gas_bar)
        toolbar.Realize()
        self.Center()

        self.Bind(wx.EVT_CLOSE, self.OnQuit)

    #----------------------------------------------------------------------
    # This function will return the proper data segment used in calculations
    def queryOptions(self, e, oreType):
        templist = {}
        a = 1
        '''print "CS: {}, FS: {}, RFS: {}".format(self.cs.IsChecked(), self.fs.IsChecked(),
                                               self.rfs.IsChecked())'''
        # If custom values, use them
        if self.cs.IsChecked():
            for key in importedData[oreType]:
                templist[a] = (key, importedData[oreType][key]['RCS'],
                               importedData[oreType][key]['CS'], str(0), str(0), str(0))
                a += 1
            return templist
        # Else.  Use the Fast/Slow split.  If you're reading this, hi!
        else:
            if self.fs.IsChecked():
                if self.rfs.IsChecked():
                    for key in importedData[oreType]:
                        templist[a] = (key, importedData[oreType][key]['RFS'],
                               importedData[oreType][key]['FS'], str(0), str(0), str(0))
                        a += 1
                    return templist
                else:
                    for key in importedData[oreType]:
                        templist[a] = (key, importedData[oreType][key]['RSS'],
                               importedData[oreType][key]['FS'], str(0), str(0), str(0))
                        a += 1
                    return templist
            else:
                if self.rfs.IsChecked():
                    for key in importedData[oreType]:
                        templist[a] = (key, importedData[oreType][key]['RFS'],
                               importedData[oreType][key]['SS'], str(0), str(0), str(0))
                        a += 1
                    return templist
                else:
                    for key in importedData[oreType]:
                        templist[a] = (key, importedData[oreType][key]['RSS'],
                               importedData[oreType][key]['SS'], str(0), str(0), str(0))
                        a += 1
                    return templist

 
    #----------------------------------------------------------------------
    def onSwitchPanels(self, Event, value):
        """"""
        if value == 1:
            #self.SetTitle("Obscenely Elaborate Yield Calculator")
            self.panel_one.Show()
            self.panel_two.Hide()
            self.panel_three.Hide()
            self.panel_four.Hide()
        elif value == 2:
            #self.SetTitle("Obscenely Elaborate Yield Calculator")
            self.panel_one.Hide()
            self.panel_two.Show()
            self.panel_three.Hide()
            self.panel_four.Hide()
        elif value == 3:
            #self.SetTitle("Obscenely Elaborate Yield Calculator")
            self.panel_one.Hide()
            self.panel_two.Hide()
            self.panel_three.Show()
            self.panel_four.Hide()
        else:
            #self.SetTitle("Obscenely Elaborate Yield Calculator")
            self.panel_one.Hide()
            self.panel_two.Hide()
            self.panel_three.Hide()
            self.panel_four.Show()
        self.Layout()

    #-----
    def OnQuit(self, event):
        self.settings_save()
        self.Destroy()

    #-----
    def Update(self, event, region):
        fetchData(1, str(self.fetch_region_numb(region)))

    #-----
    def about(self, e):
        about = 'Obscenely Elaborate Yield Calculator is a "simple" Mining-Aid for\nEveOnline players.  It is for free use and open-source for the\ncommunity, as long as the original creator is credited.\n\nPlease feel free to email suggestions!\n\n\nVersion: 1.0.1.3\nAuthor: Oey\nCode: python/wxpython\nDate: 9-25-2013\nEmail: everydayshrew@gmail.com'
        warn = wx.MessageDialog(None, about, '', wx.OK)
        ret = warn.ShowModal()

        if ret == wx.ID_OK:
            warn.Destroy()

    #-----
    def fetch_region_name(self):
        if self.jita.IsChecked(): return "Jita"
        if self.hek.IsChecked(): return "Hek"
        if self.rens.IsChecked(): return "Rens"
        if self.dodixie.IsChecked(): return "Dodixie"
        if self.amarr.IsChecked(): return "Amarr"

    #-----
    def fetch_region_numb(self, region):
        if region == "Jita": return "30000142"
        elif region == "Hek": return "30002053"
        elif region == "Rens": return "30002510"
        elif region == "Dodixie": return "30002659"
        else: return "30002187"

    #-----
    def settings_save(self):
        setfile = []
        setfile.append(self.rfs.IsChecked())
        setfile.append(self.rss.IsChecked())
        setfile.append(self.fs.IsChecked())
        setfile.append(self.ss.IsChecked())
        setfile.append(self.cs.IsChecked())
        setfile.append(self.fetch_region_name())
        settings_file = open("settings.dat", "w")
        settings_file.writelines(str(setfile))
        settings_file.close()

    #-----
    def settings_load(self):
        try:
            settings_file = open("settings.dat", "r")
        except:
            self.settings_save()
            settings_file = open("settings.dat", "r")

        settings = settings_file.readline()
        settings_file.close()
        settings = settings.replace("[","")
        settings = settings.replace("]","")
        settings = settings.replace(" ","")
        settings = settings.replace("'","")
        settings_list = settings.split(",")
        #print settings_list
        return settings_list
        
        
        
            
    
 
 
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    importedData = fetchData(0, "")
    if importedData == -1:
        warn = wx.MessageDialog(None, "You must be connected to the internet to initialize \nthis program for the first time.", 'Error Code: 1', wx.OK)
        ret = warn.ShowModal()
    elif importedData == -2:
        warn = wx.MessageDialog(None, "pulledvals.dat file has been corrupted.  Delete the file and\nrun the program again while connected to the internet.", 'Error Code: 2', wx.OK)
        ret = warn.ShowModal()
    else:
        frame = MyForm()
        frame.Show()
        app.MainLoop()
