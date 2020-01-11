from tkinter import *
import builtins
from tkinter.messagebox import askyesnocancel
from tkinter.filedialog import asksaveasfilename,askopenfilename
from keyword import kwlist
from shutil import rmtree
import os
import subprocess as sp
from trie import Trie




class Notepad(Tk):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)
        iconFile = 'py1.ico'

        self.iconbitmap(default=os.path.join(application_path, iconFile))


        self.menuItems = {"File" : ["Open", "New", "Save", "Settings", "Exit"],
                          "Edit" : ["Cut", "Copy", "Paste"],
                          "View" : ["Coming Soon..."],
                          "Help" : ["Shortcuts", "Readme", "About"]
                          }
        self.command_map={

            "list":
                [
                    "Lists all command with descriptions in OUTPUT Window",
                    self.listCommands
                ],
            "run":
                [
                    "Compiles and runs specified Program. (Python ,Java ,C/C++)",
                    self.run
                ],
            "compile":
                [
                    "Compiles specified Program. (Python ,Java ,C/C++)",
                    self.compile
                ],
            "ls":
                [
                    "Lists All Files/Folders in given Directory (Else in Present Working Directory)",
                    self.listFiles
                ],
            "pwd":
                [
                    "Shows Present Working Directory",
                    self.showDirectory
                ],
            "cd":
                [
                    "Changes Working directory. Set 'root' to flush existing pwd",
                    self.changeDirectory
                ],
            "quit" :
                [
                    "Quits the Editor without Saving anything",
                    self.exit
                ],
            "delete" :
                [
                    "Deletes the specified files (extension needed)",
                    self.delete
                ],
            "new":
                [
                    "Creates a New file in Present Working Directory.(Else specify name with location)",
                    self.newFile
                ],
            "open":
                [
                    "Opens specified files w.r.t  Present Working Directory(Else specify complete path)",
                    self.openFiles
                ]
        }
        self.activeFile = None
        # self.working_directory="/home/chandan/PycharmProjects/Editor/java_practice/sims/"
        self.working_directory="G:/anish/"
        self.openFiles=[]
        self.tabs=[]
        self.fileCache=[]
        self.searchtries=[]
        self.searchtrie=Trie()
        self.keywords = kwlist
        self.methods = dir(builtins)
        self.font_size=16
        self.font_face="Arial"
        self.font_style="Normal"
        self.linenum=""
        self.opacity=100
        self.text = None
        self.panel_frame = None
        self.outputShown=True
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()

        self.title("Notepad")
        self.wait_visibility(self)
        self.geometry(f"{self.width}x{self.height}")
        # self.geometry(f"{int(self.width / 2)}x{int(self.height)}+{int(self.width / 2)}+0")

        self.menuBar()
        self.commandPanel()
        self.tabsPanel()
        self.textArea()


        self.findnextword=""

        self.settings_window=None
        self.bind("<Control-n>", self.new)
        self.bind("<Control-o>", self.askOpen)
        self.bind("<Control-r>", self.openOutputWindow)
        self.bind("<Escape>", self.commandMode)
        self.text.bind("<Control-o>", self.askOpen)
        self.text.bind("<Control-s>", self.save)
        self.text.bind("<Control-a>", self.selectAll)
        self.text.bind("<Control-Shift-d>", self.duplicateLine)
        self.text.bind("<Control-d>", self.nextMatch)
        self.text.bind("<Control-z>", self.undo)
        self.text.bind("<Control-y>", self.redo)
        self.text.bind("<Control-Tab>", self.nextTab)
        self.text.bind("<Control-Return>", lambda x:self.run(self.activeFile.split("/")[-1], shortcut=True))
        self.text.bind("<Control-Shift-Return>", lambda x:self.compile(self.activeFile.split("/")[-1], shortcut=True))
        self.command.bind("<Tab>", self.suggest)
        self.command.bind("<Return>", self.runCommand)
        self.command.bind("<FocusOut>",self.addPlaceholder)
        self.command.bind("<FocusIn>",self.removePlaceholder)
        self.protocol("WM_DELETE_WINDOW", self.exit)

    def writeResponse(self,res):
        self.response.config(state=NORMAL)
        self.response.delete(0,END)
        self.response.insert(0, res)
        self.response.config(state=DISABLED)

    def addPlaceholder(self,*args):
        if(not self.command.get()):
            self.command.insert(0,"#Press Esc to enter a command....For all commands, run :list ")
            self.command.config(fg="#707070",font="courier 12 italic")

    def removePlaceholder(self,*args):
        self.command.delete(0,END)
        self.command.config(fg='white', font = "courier 14 normal")

    def commandMode(self,*args):
        self.command.delete(0,END)
        self.command.focus_set()

    def runCommand(self,*args):
        command = self.command.get()
        self.command.delete(0,END)
        if command[0] !=":":
            self.response.config(state=NORMAL)
            self.response.insert(0,"Command should start with : ...\n Ex ':quit -help'")
            self.response.config(state=DISABLED)
        else:
            command = command[1:].split(" ")
            print("command1",command)
            command=list(filter(lambda x: x != "", command))
            print("command2 ",command)
            fun,args = command[0],command[1:]
            print("fun , args ",fun , args)
            if len(command)==2 and args[0]=="-help":
                status=self.command_map[fun][0]
            else:
                status = self.command_map[fun][1](*args)
            self.response.config(state=NORMAL)
            self.response.delete(0,END)
            self.response.insert(0,status)
            self.response.config(state=DISABLED)

    def generateCompileRunCommand(self,file,mode="run"):
        location = self.working_directory
        if (location[-1] != "/"):
            location += "/"
        extension = file.split(".")[-1]
        command = ""
        if (extension == "py"):
            if(mode == "run"):
                command = f"python {location}{file}"
            elif(mode == "compile"):
                return False


        elif (extension == "cpp"):
            if(mode=="run"):
                command = f"cd {location} && g++ {file} -o {file.split('.')[0]} && '{location}'{file.split('.')[0]}"
            elif (mode == "compile"):
                command = f"cd {location} && g++ {file} -o {file.split('.')[0]}"


        elif (extension == "c"):
            if (mode == "run"):
                command = f"cd {location} && gcc {file} -o {file.split('.')[0]} && '{location}'{file.split('.')[0]}"
            elif(mode == "compile"):
                command = f"cd '{location}' && gcc {file} -o {file.split('.')[0]}"


        elif (extension == "java"):
            i = self.activeIndex()
            text = self.fileCache[i].lstrip()
            firstword = ""
            for ch in text:
                if (ch != " "):
                    firstword += ch
                else:
                    break
            if (firstword == "package"):
                if(mode=="run"):
                    command = f"cd {location} && javac -d . {file} && java {file.split('.')[0]}"
                elif(mode=="compile"):
                    command = f"cd {location} && javac -d . {file}"
            else:
                if (mode == "run"):
                    command = f"cd {location} && javac {file} && java {file.split('.')[0]}"
                elif (mode == "compile"):
                    command = f"cd {location} && javac {file}"



        return command

    def run(self,*args,shortcut=False):
        if(not self.outputShown):
            self.openOutputWindow()
        if (not args):
            self.output.config(state=NORMAL)
            self.output.delete(1.0, END)
            self.output.insert(1.0, "No File Selected or No Arguments were passed in command")
            self.output.config(state=NORMAL)
            return "No file Selected/ No arguements"
        file=args[0]
        if("*" in file ):
            file=file[:-1]

        command = self.generateCompileRunCommand(file=file, mode="run")
        self.writeResponse(command)
        print(command)
        output = "Make Sure all inputs are seperated by newline !!\n"
        error=""
        exit_status=""
        timeout=2
        input=self.input.get(1.0,END)
        try:
            res = sp.run(command, stdout=sp.PIPE, input=input,
                         stderr=sp.PIPE, check=True, timeout=timeout, encoding='utf-8', shell=True)

        except sp.CalledProcessError as err:
            error=err.stderr
            output=f"{err.stdout}"
            exit_status+=f"\nProcess returned with exit code {err.returncode}"
        except sp.TimeoutExpired as err:
            args = " ".join(err.args[0])
            output = err.stdout
            error=err.stderr
            exit_status=f"\nTimeoutExpired : Command '{args}' timed out after {timeout}s"
        except Exception as err:
            print("error : ",err)
            error=err
            output=""

        else:
            print("no exception : ",res)
            error=""
            output=f"{res.stdout}\n"
            exit_status = f"\nProcess returned with exit code {res.returncode}"
        finally:
            self.output.config(state=NORMAL)
            self.output.delete(1.0,END)
            self.output.insert(1.0, output)
            start = self.output.index("end-1 lines")
            self.output.insert(END, error)
            self.output.tag_add("error_msg",start,f"end-1 lines")
            start=self.output.index("end-1 lines")
            self.output.insert(END, exit_status)
            self.output.tag_add("exit_status", start, END)
            self.output.config(state=DISABLED)

            if shortcut:
                return "break"
            else:
                return command


    def compile(self,*args,shortcut=False):
        if(not self.outputShown):
            self.openOutputWindow()
        if (not args):
            self.output.config(state=NORMAL)
            self.output.delete(1.0, END)
            self.output.insert(1.0, "No File Selected or No Arguments were passed in command")
            self.output.config(state=NORMAL)
            return "No file Selected/ No arguements"

        file=args[0]
        if("*" in file ):
            file=file[:-1]

        command = self.generateCompileRunCommand(file=file, mode="compile")
        output, error, exit_status = "", "", ""
        timeout=5
        try:
            res = sp.run(command, stdout=sp.PIPE,
                         stderr=sp.PIPE, check=True, timeout=timeout, encoding='utf-8', shell=True)

        except sp.CalledProcessError as err:
            error=err.stderr
            output=f"{err.stdout}"
            exit_status+=f"\nProcess returned with exit code {err.returncode}"
        except sp.TimeoutExpired as err:
            args = " ".join(err.args[0])
            output = err.stdout
            error=err.stderr
            exit_status=f"\nTimeoutExpired : Command '{args}' timed out after {timeout}s"
        except Exception as err:
            print("error : ",err)
            error=err
            output=""

        else:
            print("no exception : ",res)
            error=""
            output=f"File Compiled Successfully.\n"
            exit_status = f"\nProcess returned with exit code {res.returncode}"
        finally:
            self.output.config(state=NORMAL)
            self.output.delete(1.0,END)
            self.output.insert(1.0, output)
            start = self.output.index("end-1 lines")
            self.output.insert(END, error)
            self.output.tag_add("error_msg",start,f"end-1 lines")
            start=self.output.index("end-1 lines")
            self.output.insert(END, exit_status)
            self.output.tag_add("exit_status", start, END)
            self.output.config(state=DISABLED)

            if shortcut:
                return "break"
            else:
                return command






    def suggest(self,*args):
        self.command.focus_set()
        command=self.command.get()
        if(command.find('"')>0):
            location=command.split('"')[1::2][0][::-1]
        else:
            location=command.split(" ")[-1][::-1]

        i=location.find("/")
        inc,location = location[:i][::-1],location[i:][::-1]
        suggestion,count="",0
        filename=""

        for file in os.listdir(location):
            if(file[0]!="." and file[:len(inc)]==inc):
                suggestion+=file+"\t"
                filename=file
                count+=1
        if(count==1):
            self.command.insert(END,filename[len(inc):]+"/")
        self.response.config(state=NORMAL)
        self.response.delete(0,END)
        self.response.insert(0,suggestion)
        self.response.config(state=DISABLED)
        self.command.focus_set()
        return "break"

    def listFiles(self,location=None):
        if(location==None):
            location=self.working_directory
        l = os.listdir(location)
        l=list(filter(lambda x:x[0]!=".", l))
        l="\t".join(l)
        return l
    def changeDirectory(self,location):
        if(location=="root"):
            location=""
        self.working_directory = location
        return f"Working Directory changed to {location}"
    def showDirectory(self):
        return f"Present Working Directory :  {self.working_directory}"

    def delete(self,*args):
        print("len ",len(args))
        print("args= ",args)
        deleted=0
        not_exist=""
        files,folders=0,0
        for filename in args:
            try:
                r=os.remove(self.getAbsolutePath(filename))
            except IsADirectoryError as e:
                try:
                    r=rmtree(self.getAbsolutePath(filename))
                except Exception as e:
                    self.output.config(state=NORMAL)
                    self.output.insert(1.0, e)
                    self.output.config(state=DISABLED)
                    not_exist += f"{filename} ,"
                else:
                    folders += 1
            except Exception as e:
                self.output.config(state=NORMAL)
                self.output.insert(1.0,e)
                self.output.config(state=DISABLED)
                not_exist+=f"{filename} ,"
            else:
                files+=1
        if(not_exist):
            not_exist=not_exist[:-1]+" Not Found !"

        res=""
        if(folders):
            res=f"{folders} Folders Deleted."
        res+= f"{files} Files Deleted. {not_exist}"
        return res

    def saveFiles(self,*args):
        pass
    def newFile(self,*args):
        i,exists,existmsg,newmsg=0,"","",""
        for file in args:
            ok = self.new(file=self.working_directory+file)
            if not ok:
                exists+=file+" ,"
            else:
                i+=1
        if(exists):
            existmsg=f"{exists[:-1]} already exists! "
        if(i):
            newmsg=f"Created {i} new files."
        return newmsg+"\t\t"+existmsg

    def openFiles(self,*args):
        count,fails=0,0
        for file in args:
            opened=self.open(self.getAbsolutePath(file))
            if(opened):
                count+=1
            else:
                fails+=1
            print(self.getAbsolutePath(file))
        return f"{count} Files Opened, {fails} Does not Exists. "
    def listCommands(self,*args):
        info=""
        for command,details in self.command_map.items():
            info+=f"{command}  :  {details[0]}\n\n"
        self.output.config(state=NORMAL)
        self.output.delete(1.0,END)
        self.output.insert(1.0,info)
        self.output.config(state=DISABLED)
        return "All Commands Listed in OUTPUT Window"
    def getAbsolutePath(self,path):
        if(path[0]=="/"):
            return path
        else:
            return self.working_directory+path

    def menuBar(self):
        mainMenu = Menu(self, bg="#212121", fg="white", bd=0)
        for name, options in self.menuItems.items():
            subMenu = Menu(mainMenu, tearoff=0)
            for option_name in options:
                fn_name = option_name.replace(" ", "_").lower()
                if (fn_name == "open"):
                    fn_name = "askOpen"
                function = getattr(self, fn_name) if fn_name in dir(self) else " "

                subMenu.add_command(label=option_name, command=function)
            mainMenu.add_cascade(label=name, menu=subMenu)
        self.config(menu=mainMenu)

    def commandPanel(self):
        frame = Frame(self, height=30, bg="#212121")

        self.command = Entry(frame, bg="#212121",fg="white", highlightthickness=0, bd=0, font="courier 14 normal",
                             insertbackground="white")
        self.addPlaceholder()
        self.command.pack(expand=1,fill=BOTH)
        frame.pack(fill=X)

    def outputWindow(self):

            self.lines.config(height=18)
            self.text.config(height=18)

            self.io_frame = Frame(self.frame, height=40)
            self.io_frame.grid(sticky="nsew", row=1, column=0, columnspan=3, rowspan=3)

            self.output_panel = Frame(self.io_frame,height=1000, bg="#212121")



            self.input_frame = Frame(self.output_panel, bg="#212121", padx=10, pady=5,highlightthickness=0)
            #
            input_label = Label(self.input_frame, text="Input", bg="#212121", fg="white")
            input_label.pack(anchor="w")
            input_scroll = Scrollbar(self.input_frame)
            input_scroll.pack(side=RIGHT, fill=Y)
            self.input = Text(self.input_frame, bg="#212121", width=30, fg="white",padx=5, font="courier 14 " \
                                                                                                          "normal",
                              insertbackground="white",yscrollcommand=input_scroll.set,highlightthickness=0)
            self.input.pack(side=LEFT)

            self.input_frame.pack(side=LEFT)

            input_scroll.config(command=self.input.yview)

            self.output_frame = Frame(self.output_panel, bg="#212121", padx=10, pady=5)
            label_frame = Frame(self.output_frame, bg="#212121")
            label_frame.pack(fill=X)

            output_label = Label(label_frame, text="Output", bg="#212121", fg="white")
            output_label.pack(side=LEFT)

            close_button = Button(label_frame, bg="#212121", bd=0,activebackground="#2B2B2B",
                                  activeforeground="white", highlightthickness=0,
                                  fg="white",text="X", command=self.closeOutputWindow)

            close_button.pack(side=RIGHT)

            output_scroll=Scrollbar(self.output_frame)
            output_scroll.pack(side=RIGHT,fill=Y)

            self.output = Text(self.output_frame, bg="#212121", fg="white", font="courier 14 normal",
                               padx=5, state=DISABLED,yscrollcommand=output_scroll.set, highlightthickness=0)
            self.output.pack(side=LEFT, fill=X,expand=1)

            self.output_frame.pack(fill=X)
            self.output_panel.pack(fill=X)


            self.output.tag_configure("error_msg", foreground='#FF2500')
            self.output.tag_configure("exit_status", font="courier 14 italic")
    def closeOutputWindow(self):
        self.io_frame.grid_forget()
        self.frame.grid_rowconfigure(0,weight=1)
        self.frame.grid_rowconfigure(1,weight=0)
        self.outputShown=False
    def openOutputWindow(self,*args):
        self.frame.grid_rowconfigure(0,weight=0)
        self.frame.grid_rowconfigure(1,weight=1)
        self.outputWindow()
        self.outputShown=True
    def autocomplete(self,word):
        self.storeCache(self.activeFile)
        text = self.fileCache[self.activeIndex()]
        wordstart=wordend=0
        words=[]
        # seperators=[",", ".", "/", " ", ":", ";", "<", ">", "[", "]", "{", "}", "(", ")", "?", "\\", "=", "+",
        #             "-", "*", "/","" "\n"]
        for i in range(len(text)):
            if (
                    (text[i] >= 'a' and text[i] <= 'z')
                    or (text[i] >= 'A' and text[i] <= 'Z')
                    or (text[i] >= '0' and text[i] <= '9')
                    or (text[i] == "-")
                    or (text[i] == "_")
            ):

                wordend+=1
            else:
                if(wordstart!=wordend):
                    w=text[wordstart:wordend]
                    self.searchtrie.add_word(w)
                    words.append(w)
                wordend=wordstart=i+1

        suggestions = self.searchtrie.prefix_words(word)
        print(suggestions)
        if(suggestions):
            self.writeResponse("\t".join(list(map(lambda x: word+x, suggestions))))
            self.text.insert("insert",suggestions[0])
            return True
        else:
            return False



    def tab(self,*args):
        word = self.text.get("insert-1c wordstart","insert")
        last_char=""
        if(word):
            last_char = word[-1]
        autocompleted=False
        if(
                ( last_char>='a' and last_char<='z') \
                or (last_char>='A' and last_char<='Z') \
                or (last_char>='0' and last_char<='9') \
                or (last_char=="-") \
                or (last_char=="_")
            ):

            word=word.strip()
            autocompleted = self.autocomplete(word)
        elif(not autocompleted):
            self.text.insert(INSERT, " " * 4)
        return 'break'

    def enter(self,*args):
        thisline = self.text.get("insert linestart","insert lineend")
        nospaceline = thisline.lstrip()
        i=len(thisline)-len(nospaceline)
        self.text.insert("insert","\n"+" "*i)
        return "break"

    def textArea(self):
        self.frame = Frame(self, bd=0, highlightthickness=0)
        self.frame.pack(fill=BOTH, expand=1)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.grid(row=0,column=2,sticky="nse")

        self.lines = Text(self.frame, width=4, bg="#333333", fg="#DCE3F4", bd=0,
                          highlightthickness=0, padx=5,yscrollcommand=self.updateScroll)
        self.lines.tag_configure('line', justify='right')
        self.lines.config(font=(self.font_face, self.font_size, self.font_style.lower()))
        self.lines.grid(row=0,column=0,sticky="nsw")

        self.text = Text(self.frame, bg="#2B2B2B", fg="white", bd=0, highlightthickness=0,padx=10,
                         insertbackground="white", yscrollcommand=self.updateScroll,
                         selectbackground="#214283",undo=True)
        self.text.config(font=(self.font_face, self.font_size, self.font_style.lower()))
        self.text.grid(row=0,column=1,sticky="nswe")

        self.frame.grid_columnconfigure(1,weight=1)

        self.outputWindow()
        res_frame = Frame(self.frame,height=20)
        self.frame.grid_rowconfigure(1,weight=1)
        self.response = Entry(res_frame, bg="#082F77", disabledbackground="#082F77", fg="white",
                              highlightthickness=0,
                              bd=0,
                              font="arial 14 normal", state=DISABLED)
        self.response.pack(fill=X, anchor="sw")
        res_frame.grid(sticky="nsew",row=4,column=0,columnspan=3,rowspan=3)

        self.text.tag_configure('orange', foreground='#FF7019')
        self.text.tag_configure('blue', foreground='blue')
        self.text.tag_configure('green', foreground='#05FF00')

        self.text.bind("<KeyRelease> ", self.textUpdated)
        self.text.bind("<Tab> ", self.tab)
        self.text.bind("<Return> ", self.enter)

        self.scrollbar.config(command=self.scrollBoth)
    def nextMatch(self,*args):
        if(not self.findnextword):
            try:
                self.findnextword = self.text.selection_get()
            except:
                return "break"
        word= self.findnextword
        index = self.text.search(word,"sel.last","end")
        if (not index):
            index = self.text.search(word,"1.0","sel.first")
        if index:
            line,col = map(int,index.split("."))
            self.text.tag_add("sel",f"{line}.{col}",f"{line}.{col+len(word)}")


        return "break"

    def allMatch(self,*args):
        if(not self.findnextword):
            self.findnextword = self.text.selection_get()
        word= self.findnextword
        text = self.text.get("1.0","end")
        length,sublen = len(text),len(word)
        line,col=1,0
        for i in range(length):
            if(text[i] == '\n'):
                line+=1
                col=0
                continue
            if(i+sublen<length):
                print(f"{line}.{col}",end=" ")
                if(text[i:i+sublen]==word):
                    self.text.tag_add("sel",f"{line}.{col}",f"{line}.{col+sublen}")
                    break

            col+=1
        print(line)
        return "break"

    def colorWord(self,word,linenum,first,last,string=False):
        start_index = f"{linenum}.{first}"
        end_index = f"{linenum}.{last}"
        if(string):
            self.text.tag_add("green", start_index, end_index)
        elif word in self.keywords:
            self.text.tag_add("orange", start_index, end_index)
        elif word in self.methods:
            self.text.tag_add("blue", start_index, end_index)

    def checkColor(self,linenum,first,last,string=False):
        start_index = f"{linenum}.{first}"
        end_index = f"{linenum}.{last}"
        if(not string):
            for tag in self.text.tag_names():
                if(tag!="sel"):
                    self.text.tag_remove(tag,start_index,end_index)

        # tagindexes = self.text.tag_nextrange("orange", start_index, end_index)
        # if tagindexes:
        #     tagend = tagindexes[1]
        #     if int(tagend.split(".")[1]) < last:
        #         self.text.tag_remove("orange", start_index, end_index)

    def lineSearch(self,linenum,line):
        first,last,i=0,0,0
        indexes = []
        string=False
        seperators=[" ", ",", "<", ">", ":", ";", "(", ")", "[", "]", "{", "}","\t"]
        linelength=len(line)
        while i<linelength:
            if line[i] == '"':
                first, i=i, i+1
                while i<linelength and line[i] != '"':
                    i+=1
                    last=i
                string=True
                self.colorWord(line[first:last+1], linenum,first, last+1, string)

            elif line[i] in seperators:
                self.colorWord(line[first:last],linenum,first,last)
                indexes.append((first, last))
                first = last = i+1
            else:
                last+=1
                self.checkColor(linenum,first,last,string)
                string=False
            i+=1



    def textUpdated(self, event=None):
        #24 => Alt, 20 =>Ctrl , 17 => Shift   these will be shortcut keys
        # print("pressed ",event.keysym,event.keycode,event.state)
        if event!=None and event=="saved":
            pass
        elif((event==None or event.state not in [17,24,20]) and event!="state" ):
            lastline = int(self.text.index("end-1c").split(".")[0])
            for i in range(1, lastline+1):
                text = self.text.get(f"{i}.0",f"{i}.end")
                self.lineSearch(i, text)
            self.updateLines(event)
            if "*" not in self.activeFile:
                for i in range(len(self.openFiles)):
                    if self.openFiles[i] == self.activeFile:
                        self.activeFile+="*"
                        self.tabs[i]["tab"].config(text=self.activeFile.split("/")[-1])

        if(event and event!="state"):
            brackets={"<": ">" , "{": "}", "(": ")","[": "]"}
            if(event.char in  brackets):
                self.text.insert("insert",brackets[event.char])
                self.text.mark_set("insert","insert-1c")



    def updateLines(self,event=None):
        # print("updating line numbers")
        if(event=="closed"):
            i=1
        else:
            i = self.text.index("end-1c").split(".")[0]
        lines = [str(j) for j in range(1, int(i) + 1)]
        self.linenum = "\n".join(lines)
        self.lines.config(state=NORMAL)
        self.lines.delete(1.0, END)
        self.lines.insert(1.0, self.linenum)
        self.lines.config(state=DISABLED)
        self.lines.tag_add("line", "1.0", "end")
        self.lines.see(self.text.index(INSERT))

    def scrollBoth(self, action, position, type=None):
        self.text.yview_moveto(position)
        self.lines.yview_moveto(position)

    def updateScroll(self, first, last, type=None):
        self.text.yview_moveto(first)
        self.lines.yview_moveto(first)
        self.scrollbar.set(first, last)

    def tabsPanel(self):
        self.panel_frame = Frame(self, height="20", bg="#212121")
        self.panel_frame.pack(fill=X)
        for file in self.openFiles:
            self.addTab(file)

    def addTab(self,newtab):
        newtabname=newtab.split("/")[-1]
        tf=Frame(self.panel_frame, bd=1, height=25, width=120, bg="#212121")
        tf.pack(fill=X, side=LEFT)
        tabs = Button(tf, text=newtabname,width=100,height=2, bg="#353535", fg="white", anchor="nw", bd=0,
                      highlightthickness=0,relief=SUNKEN, command=lambda: self.changePanel(newtab))
        close = Button(tf, text="x",width=20,height=2, bg="#353535", fg="white", anchor="nw", bd=0,padx=2,
                      highlightthickness=0,relief=SUNKEN, command=lambda: self.requestClosePanel(newtab,tf))
        close.place(in_=tf,x=100,y=0)
        tabs.place(in_=tf,x=0,y=0)
        self.tabs.append({"frame":tf, "tab":tabs, "close":close})

    def changePanel(self,tab_name):
        print("changing to panel ", tab_name)
        self.storeCache(self.activeFile)
        for i in range(len(self.openFiles)):
            if(self.openFiles[i]==tab_name):
                if(self.fileCache[i]!= "" and self.fileCache[i][-1]=='\n'):
                    self.fileCache[i]=self.fileCache[i][:-1]
                self.text.delete(1.0,END)
                self.activeFile=tab_name
                self.text.insert(1.0,self.fileCache[i])
                print("changed")
        self.show()
        self.textUpdated()
        self.updateActivePanel()

    def nextTab(self,*args):
        i = self.activeIndex()
        if(i<len(self.openFiles)-1):
            self.changePanel(self.openFiles[i+1])
        else:
            self.changePanel(self.openFiles[0])
        return "break"

    def removeStar(self,file):
        if(file!=None and file[-1]=="*"):
            file=file[:-1]
        return file
    def activeIndex(self):
        for i in range(len(self.openFiles)):
            if(self.removeStar(self.activeFile) == self.openFiles[i]):
                return i

        return -1

    def updateActivePanel(self):
        i=self.activeIndex()
        print(i)
        for j in range(len(self.tabs)):
            if(j==i):
                self.tabs[i]['tab'].config(bg="#808080")
                self.tabs[i]['close'].config(bg="#808080")
            else:
                self.tabs[j]['tab'].config(bg="#353535")
                self.tabs[j]['close'].config(bg="#353535")

    def closePanel(self,tab_name,tf):
        i,length=0,len(self.openFiles)
        index=-1
        while i < length:
            if (self.openFiles[i] == tab_name):
                del self.fileCache[i]
                del self.openFiles[i]
                del self.tabs[i]
                index=i
                length-=1
            i+=1
        tf.pack_forget()
        if(index!=0):
            index-=1
        if(self.activeFile == tab_name and self.openFiles):
            self.text.delete("1.0", END)
            self.activeFile=self.openFiles[index]
            self.text.insert(1.0,self.fileCache[index])
        self.updateLines(event="closed")
        self.updateActivePanel()



    def requestClosePanel(self,tab_name,tf):
        print("closing  panel ", tab_name)
        if("*" in self.activeFile):
            self.askSave(tab_name,tf)
        else:
            self.closePanel(tab_name,tf)
    def askSave(self,tab_name,tf):
        choice = askyesnocancel("Save Warning!",
                                "You were exitting without saving your progress.Do you want to Save>")
        if(choice==True):
            self.save()
        if(choice != None):
            self.closePanel(tab_name,tf)



    def askOpen(self,*args):
        print("Opening File")
        print("caching... ",self.text.get(1.0,END))

        file = askopenfilename(defaultextension=".txt",
                                          filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")],
                                          initialdir=self.working_directory
                                        )

        if file:
            self.open(file)
        return "break"


    def save(self,event=None):
        if("*" in self.activeFile):
            self.activeFile = self.activeFile[:-1]
        print("Saving ",self.activeFile)
        newfile = "/" not in self.activeFile
        temp=False
        if newfile:
            temp = asksaveasfilename(initialfile="Untitled.txt" ,
                                     defaultextension=".txt",
                                     filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]
                                    )
            if(temp):
                i=self.activeIndex()
                self.openFiles[i]=temp
                self.activeFile = temp
                print("active file is now ", self.activeFile)
                print("content in  file is :  ", self.text.get(1.0, END))

        if(not newfile or temp):
            f = open(self.activeFile, "w")
            f.write(self.text.get(1.0, END))
            f.close()
        print("now : ",self.activeFile)
        for i in range(len(self.openFiles)):
            if(self.openFiles[i]==self.activeFile):
                self.tabs[i]["tab"].config(text=self.activeFile.split("/")[-1])
        self.title(self.activeFile.split("/")[-1] + " - Notepad")
        self.textUpdated(event="saved")

    def open(self,file):
        exists=self.checkPath(file)
        if(exists==True):
            f = open(file, "r")
            text = f.read()
            self.storeCache(self.activeFile)
            self.text.delete(1.0,END)
            self.text.insert(1.0, text)
            self.fileCache.append(text)
            self.searchtries.append(Trie())
            self.openFiles.append(file)
            self.addTab(file)
            self.title(file.split("/")[-1] + " - Notepad")
            self.activeFile=file
            self.updateLines()
            self.textUpdated()
            self.text.edit_reset()
            if("*" in self.activeFile):
                self.activeFile=self.activeFile[:-1]
            self.updateActivePanel()
            return True
        else:
            return False


    def storeCache(self,tab_name):
        # print("length open files :",len(self.openFiles))
        # print("length files cache :",len(self.fileCache))
        # print("length Tabs :",len(self.tabs))
        # print("tabname",tab_name)
        for i in range(len(self.openFiles)):
            if(self.openFiles[i]==self.removeStar(tab_name)):
                self.fileCache[i]=self.text.get(1.0,END)
        self.show()



    def new(self,*args,file=None):
        if(self.activeFile):
            self.storeCache(self.activeFile)
            self.text.delete(1.0, END)
            print("file",file)

        if(file):
            if(os.path.isfile(file)):
                return False
            else:
                f = open(file,"w")
                new_file_name=file
        else:
            new_file_name="Untitled"
            i=1
            found=0
            while not found:
                found=1
                for file in self.openFiles:
                    if new_file_name in file:
                        new_file_name = "Untitled-"+str(i)
                        i+=1
                        found=0
                        break
        print("found a new file name ", new_file_name)
        self.openFiles.append(new_file_name)
        self.activeFile=new_file_name
        self.fileCache.append("")
        self.searchtries.append(Trie())
        self.addTab(new_file_name)
        self.title(str(new_file_name)+" - Notepad")
        self.show()
        self.updateActivePanel()
        self.updateLines();
        return "break"
    def checkPath(self,path):
        if(os.path.isfile(path) or os.path.exists(path)):
            return True
        else:
            return "File or Directory Does not Exists!"

    def selectAll(self,*args):
        # self.text.tag_add("sel",1.0,END)
        self.text.tag_add(SEL, "1.0", END)
        self.text.mark_set(INSERT,"1.0")
        return "break"

    def duplicateLine(self,*args):
        curr_linenum = int(self.text.index(INSERT).split(".")[0])
        curr_line=self.text.get(f"{curr_linenum}.0",f"{curr_linenum}.end")+"\n"
        print(curr_linenum)
        print(curr_line)
        self.text.insert(f"{curr_linenum}.0",curr_line)
        self.textUpdated()
        return "break"

    def undo(self,*args):
        print("redo")
        try:
            self.text.edit_undo()
        except TclError:
            print("Cant Undo")
        return "break"


    def redo(self,*args):
        try:
            print(self.text.edit_redo())
        except TclError:
            print("nothing to redo")
        return "break"

    def show(self):
        pass
        # print("ACTIVE FILE : ", self.activeFile)
        # print("OPEN FILES : ", self.openFiles)
        # print("CAched FILES : ", self.fileCache)

    def settings(self):
        print("Opening Settings window")
        self.settings_window=Settings(self)
        self.settings_window.done()
    def exit(self):
        print("closing settings first")
        if (self.settings_window != None):
            self.settings_window.quit()
            self.settings_window = None
        self.quit()
        return "Exit"


    def readme(self):
        print("works")

    def about(self):
        print("works")

    def shortcuts(self):
        print("works")

    def done(self):
        self.mainloop()



class Settings(Tk):
    def __init__(self,notepad):
        super().__init__()
        self.notepad=notepad
        self.b=IntVar()
        self.title("Settings")
        self.geometry(f"{int(notepad.width/2)}x{int(notepad.height)}+{int(notepad.width/2)}+0")
        self.categories = ["Appearance", "Editor"]
        self.font_size_options=[i for i in range(8,48)]
        self.font_face_options=["Arial", "Courier", "Times", "courier"]
        self.font_style_options=["Normal", "Bold", "Italic", "Bold Italic"]
        self.activeTab=None
        self.tabsPanel()
        self.mainarea()

    def tabsPanel(self):
        self.panel_frame = Frame(self, height="20", bg="#212121")
        self.panel_frame.pack(fill=X)
        for c in self.categories:
            tf = Frame(self.panel_frame, bd=1, height=25, width=125, bg="#212121")
            tf.pack(fill=X, side=LEFT)
            tabs = Button(tf, text=c, width=12, height=2, bg="#353535", fg="white", anchor="nw", bd=0,
                          highlightthickness=0, relief=SUNKEN, command=lambda: 1)
            tabs.place(in_=tf, x=0, y=0)
        self.activeTab=self.categories[0]

    def mainarea(self):
        frame=Frame(self,bg="#2B2B2B", padx=25, pady=25)
        frame.pack(fill=BOTH, expand=1)
        if(self.activeTab == "Appearance"):
            self.appearance(frame)


    def appearance(self,frame):
        #FONTS SETTINGS
        font_frame =  Frame(frame, bg="#444749", padx=10, pady=10)
        Label(font_frame, text="FONTS", bg="#444749", fg="white", font="arial 20 bold").grid()

        # FONT SIZE
        Label(font_frame, text="Font Size : ", bg="#444749", fg="white", font="arial 16 italic", padx=5, pady=5).grid(
            row=2,column=2)
        self.font_size = Combobox(font_frame, values=self.font_size_options, width=10)
        self.font_size.set(self.notepad.font_size)
        self.font_size.bind("<<ComboboxSelected>>",self.change)
        self.font_size.grid(row=2,column=3)

        # FONT FACE
        Label(font_frame, text="Font Face : ", bg="#444749", fg="white", font="arial 16 italic", padx=5, pady=5).grid(row=3,column=2)
        self.font_face = Combobox(font_frame, values=self.font_face_options, width=10)
        self.font_face.set(self.notepad.font_face)
        self.font_face.bind("<<ComboboxSelected>>", self.change)
        self.font_face.grid(row=3, column=3)

        #FONT STYLE
        Label(font_frame, text="Font Style : ", bg="#444749", fg="white", font="arial 16 italic", padx=5, pady=5).grid(row=4,column=2)
        self.font_style = Combobox(font_frame, values=self.font_style_options, width=10)
        self.font_style.set(self.notepad.font_style)
        self.font_style.bind("<<ComboboxSelected>>", self.change)
        self.font_style.grid(row=4, column=3)


        font_frame.pack(fill=X,pady=10)


        #THEME SETTINGS
        theme_frame = Frame(frame, bg="#444749", padx=10, pady=10)
        Label(font_frame, text="THEMES", bg="#444749", fg="white", font="arial 20 bold").grid()

        #OPACITY
        Label(theme_frame, text="Window Opacity : ", bg="#444749", fg="white", font="arial 16 italic",
              padx=5,pady=5).grid(row=2, column=2)
        opacity = Scale(theme_frame, from_=0, to=100, orient=HORIZONTAL, tickinterval=25, length=400, bg="#444749",
                        fg="white",  highlightthickness=0, command=self.changeOpacity)
        opacity.set(self.notepad.opacity)
        opacity.grid(row=2,column=3)

        theme_frame.pack(fill=X, pady=10)

    def changeOpacity(self,opacity):
        print(opacity)
        self.notepad.opacity = opacity
        self.notepad.attributes("-alpha",float(float(opacity)/100.0))
    def change(self,event):
        self.notepad.font_size=self.font_size.get()
        self.notepad.font_style=self.font_style.get()
        self.notepad.font_face=self.font_face.get()
        self.notepad.text.configure(font=(self.notepad.font_face, self.notepad.font_size,
                                          self.notepad.font_style.lower()))
        self.notepad.lines.configure(font=(self.notepad.font_face, self.notepad.font_size,
                                          self.notepad.font_style.lower()))




    def done(self):
        self.mainloop()



w=Notepad()

w.new()
w.done()
