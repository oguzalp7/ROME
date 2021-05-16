from tkinter import *

class Window(object):

    def __init__(self,window):

        self.window = window

        self.window.wm_title("BlinkEye")

        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

	#configuring the input fields
        l1=Label(window,text="Patient Name")
        l1.grid(row=0,column=0)

        l2=Label(window,text="Patient Surname")
        l2.grid(row=1,column=0)

        l2=Label(window,text="Patient id")
        l2.grid(row=1,column=2)

	#setting up the entry fields for user input
        self.title_text=StringVar()
        self.e1=Entry(window,textvariable=self.title_text)
        self.e1.grid(row=0,column=1)

        self.author_text=StringVar()
        self.e2=Entry(window,textvariable=self.author_text)
        self.e2.grid(row=1,column=1)

        self.title_text=StringVar()
        self.e1=Entry(window,textvariable=self.title_text)
        self.e1.grid(row=1,column=3)

        self.list1=Listbox(window, height=24,width=70)
        self.list1.grid(row=2,column=0,rowspan=6,columnspan=2)

        sb1=Scrollbar(window)
        sb1.grid(row=2,column=2,rowspan=6)

        self.list1.configure(yscrollcommand=sb1.set)
        sb1.configure(command=self.list1.yview)

        self.list1.bind('<<ListboxSelect>>',self.get_selected_row)

	#here is where I add the buttons of the GUI. The row number can be used to change the order of the buttons
        b1=Button(window,text="View all", width=12,command=self.view_command)
        b1.grid(row=2,column=3)

        b2=Button(window,text="Search name", width=12,command=self.search_command)
        b2.grid(row=3,column=3)

        b2=Button(window,text="Search id", width=12,command=self.search_command)
        b2.grid(row=4,column=3)

        b3=Button(window,text="Delete selected", width=12,command=self.delete_command)
        b3.grid(row=5,column=3)

        b4=Button(window,text="View Results", width=12,command=self.delete_command)
        b4.grid(row=6,column=3)

        b5=Button(window,text="View Graphs", width=12,command=self.delete_command)
        b5.grid(row=7,column=3)

        b6=Button(window,text="Close", width=12,command=window.destroy)
        b6.grid(row=8,column=3)

    #here is where I capture the input of the empty field
    def get_selected_row(self,event):
        if len(self.list1.curselection())>0:
            index=self.list1.curselection()[0]
            self.selected_tuple=self.list1.get(index)
            self.e1.delete(0,END)
            self.e1.insert(END,self.selected_tuple[1])
            self.e2.delete(0,END)
            self.e2.insert(END,self.selected_tuple[2])
            self.e3.delete(0,END)
            self.e3.insert(END,self.selected_tuple[3])
            self.e4.delete(0,END)
            self.e4.insert(END,self.selected_tuple[4])

    #These are the functions called by their respective buttons. 
    #Orignally These were going to be used to query the database and output results however due to time constraints they don't work at the moment.
    def view_command(self):
        pass

    def search_command(self):
        pass

    def add_command(self):
        pass

    def delete_command(self):
        pass

    def update_command(self):
        pass

def main():
    window=Tk()
    window.geometry("700x520")
    Window(window)
    window.mainloop()
