# Εισαγωγή απαραίτητων Module
import sqlite3
import random
import time
import customtkinter as Ctk
import pygame
from PIL import Image
# import WWTBAM_Questions

# WWTBAM_Questions.conn.cursor()
# Σύνδεση με τη βάση
conn = sqlite3.connect("questions.db") 
cursor = conn.cursor() 

# Μεταβλητή για το path των Resources
Filepath = "Resourses/"

# Mixer Initialization
pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
pygame.mixer.init()

# Δημιουργία πίνακα παικτών στην βάση για να αποθηκεύονται τα στατιστικα
cursor.execute('''CREATE TABLE IF NOT EXISTS player_Stats (
                   PlayerName TEXT,
                   TotalQuestions INTEGER,
                   CorrectAnswers INTEGER,
                   PrizeMoney INTEGER,
                   TotalTime REAL,
                   TotalSeconds INTEGER
                )''')

# Επιλογή theme (επιλογές: "light","dark","default")
Ctk.set_appearance_mode ("Dark")

# Δημιοργία instance CTk
App = Ctk.CTk() 

# Επιλογή favicon παραθύρου
App.iconbitmap(Filepath+"hero_ico.ico")

# Όνομα παραθύρου
App.title("Ποιος θέλει να γίνει εκατομμυριούχος")

# Μέγεθος παραθύρου
App.geometry("380x750") 

# Επιλογή για το αν θα γίνεται αλλαγή μεγέθους παραθύρου (x,y)
App.resizable (False,False)

# Main Class - Κύρια κλάση
class Millionaire:
    def __init__(self, master):
# Instance Variables        
        self.master = master
        self.QuestionNumber = 1 
        self.PrizeMoney = 0 
        self.AskedQuestionIds = []
        self.QuestionData = [] 
        self.WrongAnswerCount = 0 
        self.StartTime = None
        self.TotalSeconds = 0
        self.EndTime = None  
        self.TimerId = None
        self.TotalQuestions = 0
        self.CorrectAnswers = 0
        self.PlayerName = ""
        self.LifelinesUsed = {
            "50-50": False,
            "Αντικατάσταση Ερώτησης": False, 
            "Δείξε μου τη Σωστή απάντηση": False
        }
        self.CounterImages = []

        #---------------------------------------------------------------------------------------------------------
        # Player Name GUI (γραφιστικό για εισαγωγή ονόματος)
        self.LoginPictureFrame = Ctk.CTkFrame (self.master,width=380, height=750)
        self.LoginPicture = Ctk.CTkImage (dark_image=Image.open(Filepath+"bg_gradient.jpg"),size=(380,750))
        self.LoginPictureLabel = Ctk.CTkLabel (self.LoginPictureFrame,image=self.LoginPicture,text="")
        self.LoginFrame = Ctk.CTkFrame(self.master, width=380, height=214)
        self.LoginLabel = Ctk.CTkLabel(self.LoginFrame, text="Δώσε το όνομά σου:")
        self.PlayerName = Ctk.CTkEntry(self.LoginFrame,width=180, textvariable=self.PlayerName,
                                       placeholder_text="Όνομα εκατομμυριούχου",bg_color="transparent")
        
        self.LoginButton = Ctk.CTkButton(self.LoginFrame, text="Παίξε!!!", command=self.MillionairesName)
        
        # Player Name GUI Geometry Manager (για γραφιστικό εισαγωγής ονόματος)
        self.LoginLabel.pack (side="top",pady=5) 
        self.PlayerName.pack(side="top")  
        self.LoginButton.pack(side="top",pady=10)  
        self.LoginFrame.pack()
        self.LoginFrame.place_configure (relx=0.5, rely=0.3,relwidth=2, anchor="center")
        self.LoginPictureLabel.pack(side="top")
        self.LoginPictureFrame.pack(side="top")

        #---------------------------------------------------------------------------------------------------------
        # Main GUI (Κυρίως γραφιστικό)
        self.PictureFrame = Ctk.CTkFrame (self.master,width=320, height=214, fg_color="transparent")
        self.MainImage = Ctk.CTkImage (dark_image=Image.open(Filepath+"logo_resized.png"),size=(214,214))
        self.MainPictureLabel = Ctk.CTkLabel (self.PictureFrame,image=self.MainImage,text="")

        self.InsertQuestionsDBBtnPicture = Ctk.CTkImage (dark_image=Image.open(Filepath+"data_entry_resized.png"),size=(24,24))
        self.InsertQuestionsDBBtn = Ctk.CTkButton (self.PictureFrame,width=32, 
                                                   height=32,image=self.InsertQuestionsDBBtnPicture,text="")
        self.StatsBtnPicture = Ctk.CTkImage (dark_image=Image.open(Filepath+"stats.png"),size=(24,24))
        self.StatsBtn = Ctk.CTkButton (self.PictureFrame, width=32, 
                                       height=32,image=self.StatsBtnPicture, text="")

        self.CountDownTimerImages()

        self.CounterFrame = Ctk.CTkFrame (self.master, width=96, height=94,fg_color="transparent")
        self.TimeFrameImage = Ctk.CTkImage (dark_image=Image.open(Filepath+"time_frame.png"),size=(96,94))
        self.TimeFrameLabel = Ctk.CTkLabel (self.CounterFrame,image=self.TimeFrameImage, text="")
        self.TensLabel = Ctk.CTkLabel (self.CounterFrame, image=self.CounterImages[0],text="")
        self.OnesLabel = Ctk.CTkLabel (self.CounterFrame, image=self.CounterImages[0], text="")

        self.TimeFrameLabel.place (relx=0.5, rely=0.5,anchor="center")
        self.TensLabel.place (relx=0.41, rely=0.5, anchor="center")
        self.OnesLabel.place (relx=0.62, rely=0.5, anchor="center")

        self.PrizeLabelImage = Ctk.CTkImage(dark_image=Image.open(Filepath+"prize_frame.png"),size=(380,47))
        self.PrizeLabel = Ctk.CTkLabel(self.master, text="",image=self.PrizeLabelImage,font=("arial",20,"bold"),text_color="#d4af37") 

        self.QuestionLabelImage = Ctk.CTkImage (dark_image=Image.open(Filepath+"question_frame.png"),size=(380,65))
        self.QuestionLabel = Ctk.CTkLabel(self.master,wraplength=300,image=self.QuestionLabelImage,text="",font=("Tahoma",13.5))
        self.Option_A_Button = Ctk.CTkButton(self.master, width=220, height=30,text="",
                                             border_color="silver",border_width=3)
        self.Option_B_Button = Ctk.CTkButton(self.master, width=220, height=30,text="",
                                             border_color="silver",border_width=3)
        self.Option_C_Button = Ctk.CTkButton(self.master, width=220, height=30,text="",
                                             border_color="silver",border_width=3)
        self.Option_D_Button = Ctk.CTkButton(self.master, width=220, height=30,text="",
                                             border_color="silver",border_width=3)
        
        # Main Gui Geometry Manager (για το κυρίως γραφιστικό)
        self.PictureFrame.pack(side="top", expand="true")
        self.InsertQuestionsDBBtn.pack(side="left", expand="true",padx=19,anchor="nw")
        self.StatsBtn.pack (side="right",expand="true",padx=19,anchor="ne")
        self.MainPictureLabel.pack (side="top")
        self.CounterFrame.pack (side="top", pady=15)
        self.PrizeLabel.pack()
        self.QuestionLabel.pack(side="top",pady=10)
        self.Option_A_Button.pack(pady=7)
        self.Option_B_Button.pack(pady=7)
        self.Option_C_Button.pack(pady=7)
        self.Option_D_Button.pack(pady=7)
        
        self.LifeLinesFrame = Ctk.CTkFrame (self.master,width=280,height=90,fg_color="transparent")
        self.LifeLinesFrame.pack(pady=15)
        
        # LifeLines Buttons and Geometry Manager (γραφιστικό για τις βοήθειες)
        self.FiftyFiftyImage = Ctk.CTkImage(dark_image=Image.open(Filepath+"5050.png"),size=(70,50))
        self.FiftyFiftyImageUsed = Ctk.CTkImage(dark_image=Image.open(Filepath+"5050_used.png"),size=(70,50))
        self.FiftyFiftyButton = Ctk.CTkButton(self.LifeLinesFrame, text="", image=self.FiftyFiftyImage,
                                              fg_color="transparent",hover_color="#242424",
                                              width=70, height=50,command=self.FiftyFifty,)
        self.FiftyFiftyButton.pack(side="left", expand="true",padx=7)
        
        self.ReplaceQuestionImage = Ctk.CTkImage(dark_image=Image.open(Filepath+"replace_question.png"),size=(70,50))
        self.ReplaceQuestionImageUsed = Ctk.CTkImage(dark_image=Image.open(Filepath+"replace_question_used.png"),size=(70,50))
        self.RepalceQuestionButton = Ctk.CTkButton(self.LifeLinesFrame, text="", image=self.ReplaceQuestionImage, 
                                                   fg_color="transparent", hover_color="#242424",
                                                   width=70, height=50,command=self.ReplaceQuestion)
        self.RepalceQuestionButton.pack(side="left",expand="true",padx=7)
        
        self.SuggectCorrectAnswerImage = Ctk.CTkImage (dark_image=Image.open(Filepath+"show_answer.png"),size=(70,50))
        self.SuggectCorrectAnswerImageUsed = Ctk.CTkImage (dark_image=Image.open(Filepath+"show_answer_used.png"),size=(70,50))
        self.SuggestCorrectButton = Ctk.CTkButton(self.LifeLinesFrame, text="", image=self.SuggectCorrectAnswerImage,
                                                  fg_color="transparent",hover_color="#242424",
                                                  width=70, height=50, command=self.SuggestCorrectAnswer)
        self.SuggestCorrectButton.pack(side="left",expand="true",padx=7)

#----------------------------------------------------------------------------------------------------------        
# Method για εισαγωγή ονόματος παίκτη
    def MillionairesName (self):
        global PlayerName
        PlayerName = self.PlayerName.get()
        if PlayerName == "":
            PlayerName = "Άγνωστος"
        self.LoginPictureFrame.destroy()
        self.LoginFrame.destroy()
        print (PlayerName)
        self.TensLabel.configure (image=self.CounterImages[0])
        self.OnesLabel.configure (image=self.CounterImages[0])  
        self.PlayAnySound ("audio_lets-play.mp3")
        self.StartTimer(60) 
        self.StartTime = time.time ()
        
# Method για εισαγωγή των custom αριθμών του timer στη λίστα που τους περιέχει           
    def CountDownTimerImages (self):
        for Counter in range(10):
            CounterImage = Image.open(Filepath+f"{Counter}_blue3.png")
            self.CounterImages.append(Ctk.CTkImage(CounterImage,size=(26,26)))

# Method για το παίξιμο Μουσικής 
    def PlayAnySound(self,SoundToPlay):  #playing Ticking Sound
        pygame.mixer.music.load(SoundToPlay)
        pygame.mixer.music.set_volume(0.5) #range b/w 0 to 1
        pygame.mixer.music.play(-1)
      

 # Method επαναφοράς των κουμπιών των απαντήσεων στην αρχική τους κατάσταση       
    def EnableButtons (self):
        self.Option_A_Button.configure(state=Ctk.ACTIVE,fg_color=("#3a7ebf", "#1f538d"))
        self.Option_B_Button.configure(state=Ctk.ACTIVE,fg_color=("#3a7ebf", "#1f538d"))
        self.Option_C_Button.configure(state=Ctk.ACTIVE,fg_color=("#3a7ebf", "#1f538d"))
        self.Option_D_Button.configure(state=Ctk.ACTIVE,fg_color=("#3a7ebf", "#1f538d"))

 # Method για βοήθεια 50/50           
    def FiftyFifty(self):
        if self.LifelinesUsed["50-50"]: 
            return
        self.LifelinesUsed["50-50"] = True 
        Options = [self.QuestionData[2], self.QuestionData[3], self.QuestionData[4], self.QuestionData[5]] 
        CorrectOption = Options.pop(Options.index(Answer)) 
        IncorrectOptions = [Option for Option in Options if Option != CorrectOption] 
        DisabledOptions = random.sample(IncorrectOptions, 2) 
        if self.Option_A_Button.cget("text")[3:] in DisabledOptions: 
            self.Option_A_Button.configure(state=Ctk.DISABLED)
        else:
            self.Option_A_Button.configure(command=lambda:self.CheckAnswer(self.Option_A_Button.cget("text")[3:])) 
        if self.Option_B_Button.cget("text")[3:] in DisabledOptions:
            self.Option_B_Button.configure(state=Ctk.DISABLED)
        else:
            self.Option_B_Button.configure(command=lambda:self.CheckAnswer(self.Option_B_Button.cget("text")[3:]))
        if self.Option_C_Button.cget("text")[3:] in DisabledOptions:
            self.Option_C_Button.configure(state=Ctk.DISABLED)
        else:
            self.Option_C_Button.configure(command=lambda:self.CheckAnswer(self.Option_C_Button.cget("text")[3:]))
        if self.Option_D_Button.cget("text")[3:] in DisabledOptions:
            self.Option_D_Button.configure(state=Ctk.DISABLED)
        else:
            self.Option_D_Button.configure(command=lambda:self.CheckAnswer(self.Option_D_Button.cget("text")[3:]))
        self.FiftyFiftyButton.configure(state=Ctk.DISABLED,image=self.FiftyFiftyImageUsed,fg_color="transparent")

# Method για βοήθεια "Αλλαγή ερώτησης"
    def ReplaceQuestion(self):
        if self.LifelinesUsed["Αντικατάσταση Ερώτησης"]: 
            return
        self.LifelinesUsed["Αντικατάσταση Ερώτησης"] = True 
        self.GetQuestion() 
        self.DisplayQuestion()
        self.RepalceQuestionButton.configure(state=Ctk.DISABLED,image=self.ReplaceQuestionImageUsed,fg_color="transparent") 

# Method για βοήθεια "Δείξε μου τη σωστή απάντηση"
    def SuggestCorrectAnswer(self):
        if self.LifelinesUsed["Δείξε μου τη Σωστή απάντηση"]: 
            return
        self.LifelinesUsed["Δείξε μου τη Σωστή απάντηση"] = True 
        for button in [self.Option_A_Button, self.Option_B_Button, self.Option_C_Button, self.Option_D_Button]:
            if button.cget ("text")[3:] != Answer:
                button.configure(state=Ctk.DISABLED)
            else:
                 button.configure (fg_color="green") 
        self.SuggestCorrectButton.configure(state=Ctk.DISABLED,image=self.SuggectCorrectAnswerImageUsed,fg_color="transparent") 

# Method για την επιλογή ερώτησης από της βάση (επίπεδο, μοναδικότητα)
    def GetQuestion(self):
        global Answer 
        if self.QuestionNumber <= 5: 
            cursor.execute("SELECT * FROM questions WHERE level=1 AND id NOT IN ({})"
                           .format(",".join("?"*len(self.AskedQuestionIds))), self.AskedQuestionIds)
        elif self.QuestionNumber <= 10 and self.QuestionNumber >= 6: 
            cursor.execute("SELECT * FROM questions WHERE level=2 AND id NOT IN ({})"
                           .format(",".join("?"*len(self.AskedQuestionIds))), self.AskedQuestionIds)
        else:
            cursor.execute("SELECT * FROM questions WHERE level=3 AND id NOT IN ({})"
                           .format(",".join("?"*len(self.AskedQuestionIds))), self.AskedQuestionIds)
        AllQuestions = cursor.fetchall() 

        if len(AllQuestions) == 0: 
            return
        self.QuestionData = random.choice(AllQuestions) 
        self.AskedQuestionIds.append(self.QuestionData[0]) 
        Answer = self.QuestionData[6] 
        self.TensLabel.configure (image=self.CounterImages[0])
        self.OnesLabel.configure (image=self.CounterImages[0])  
        self.StartTimer(60) 
        
# Method για την εμφάνιση της επιλεγμένης ερώτησης
    def DisplayQuestion(self): 
        self.EnableButtons ()
        self.QuestionLabel.configure(text=self.QuestionData[1]) 
        Options = [self.QuestionData[2], self.QuestionData[3], self.QuestionData[4], self.QuestionData[5]] 
        random.shuffle(Options) 
        
        self.Option_A_Button.configure(
                                        text=f"Α: {Options[0]}", 
                                        command=lambda: (self.Option_A_Button.configure(fg_color="orange"), 
                                        self.Option_A_Button.after(5000, self.CheckAnswer, Options[0]))
                                        )

        # self.Option_A_Button.configure(text=f"Α: {Options[0]}", command=lambda:self.CheckAnswer(Options[0])) 
        self.Option_B_Button.configure(text=f"Β: {Options[1]}", command=lambda:self.CheckAnswer(Options[1]))
        self.Option_C_Button.configure(text=f"Γ: {Options[2]}", command=lambda:self.CheckAnswer(Options[2]))
        self.Option_D_Button.configure(text=f"Δ: {Options[3]}", command=lambda:self.CheckAnswer(Options[3]))
        self.PrizeLabel.configure(text=f"{self.PrizeMoney} €") 
        
# Method για τον έλεγχο της απάντησης
    def CheckAnswer(self, ChosenOption):
        
        if ChosenOption == Answer: 
            self.TotalQuestions += 1 
            self.CorrectAnswers += 1 
            self.TotalSeconds += int(time.time() - self.StartTime) 
            PrizeList = [0, 100, 200, 300, 500, 1000, 2000, 4000, 8000, 16000, 32000, 50000, 100000, 250000, 500000, 1000000] 
            self.PrizeMoney = PrizeList[self.CorrectAnswers] 
            self.QuestionNumber += 1 
            self.PrizeLabel.configure(text=f"{self.PrizeMoney} €") 
            if self.CorrectAnswers == 15 : 
                self.WriteStatistics() 
                self.master.destroy() 
            else:
                self.GetQuestion() 
                self.DisplayQuestion() 
        else:
            self.WrongAnswerCount += 1 
            self.TotalQuestions += 1 
            if self.WrongAnswerCount == 3: 
                self.WriteStatistics() 
                self.master.destroy() 
            else:
                self.GetQuestion() 
                self.DisplayQuestion()

# Method για την έναρξη του χρόνου        
    def StartTimer(self, TimeRemaining):
        if self.TimerId is not None:  
            self.master.after_cancel(self.TimerId)
            self.TimerId = None
        if TimeRemaining == 0: 
            self.WrongAnswerCount += 1
            if self.WrongAnswerCount == 3:
                self.WriteStatistics()
                self.master.destroy ()
            else:
                self.GetQuestion() 
                self.DisplayQuestion()
        else:
            Tens = TimeRemaining // 10
            Ones = TimeRemaining % 10
            self.TensLabel.configure (image=self.CounterImages[Tens])
            self.TensLabel._image = self.CounterImages[Tens]
            self.TensLabel.configure (compound="center")
            self.OnesLabel.configure (image=self.CounterImages[Ones])
            self.OnesLabel._image = self.CounterImages[Ones]
            self.OnesLabel.configure (compound = "center") 
            self.TimerId = self.master.after (1000, self.StartTimer, TimeRemaining-1)

# Method για την εγγραφή των στατιστικών στην βάση    
    def WriteStatistics(self):
        if self.StartTime is None:
            return
        self.EndTime = time.time()
        TotalTime = self.EndTime - self.StartTime
        self.TotalSeconds = int(TotalTime)
        TotalTime = round((self.TotalSeconds / 60), 2)
        Stats = (PlayerName, self.TotalQuestions, self.CorrectAnswers, self.PrizeMoney, TotalTime, self.TotalSeconds)
        cursor.execute('INSERT INTO player_Stats VALUES (?, ?, ?, ?, ?, ?)', Stats)
        conn.commit()

# Main
game = Millionaire(App)

game.GetQuestion()
game.DisplayQuestion()
App.mainloop()