'''Imports and Variables'''
from tkinter import *
import keyboard #pip install keyboard
import pygame #pip3 install pygame
import math, random

#game size
canvasHeight = 500
canvasWidth = 600
cellSize = 20

#colors for the GUI
colorLight = "#FFFFFF"
colorMid = "#4A3B72"
colorDark = "#110C1E"

#FIXME: whenever one of these updates, update the label's text AND replace it to (origNum + (len(str(var)) * 8))
score = 0
level = 1
lines = 0

gameOn = True
sound = True
blocks = [] #holds all of the tetrisBlock() objects
cubeList = []
tempCubeList = []
blockColors = ["#00FFFF", "#0000FF", "#FFAA00", "#FFFF00", "#00FF00", "#AA00FF", "#FF0000"]
processingBlock = False

gameLines = [] #Holds the lines on the board
upNextBox = 0
board = 0
coverGameLines = []
coverUpNextBox = 0
coverBoard = 0
volumeButton = 0
levelSlider = 0
totalBlocks = 0

'''FIXME NOTE'''
#OPTIONAL Adjust block and GUI colors, they're kinda ugly right now
#OPTIONAL Press 'c' to hold a block for later?

#FEATURE "Next" display (Will have to rework random so the next one can be predicted)

#ERROR Make game stop right when the top is reached and delete the class objects (starting over will 
# recreate these)
#ERROR Left side of the screen doesn't detect the bottom right (Never with long blues for some reason)

'''classes'''
class tetrisBlock: #Creates a block
    def __init__(self):
        self.type = random.randint(0, 0) #Randomizes one of the tetris block types
        self.color = blockColors[self.type]
        self.cubes = [] #Holds all of the tetrisCube() objects
        self.blockState = 1 #0 = Resting, 1 = Falling, 2 = Being held (idk if I'll implement this one)
        self.randID = random.randint(100000, 999999) #A random id to identify this block from another
        self.rotation = 0

        #Hotkeys so that the game can react when these keys are pressed
        keyboard.add_hotkey("left", lambda: self.moveBlock("left"))
        keyboard.add_hotkey("right", lambda: self.moveBlock("right"))
        keyboard.add_hotkey("down", lambda: self.moveBlock("down"))
        keyboard.add_hotkey("up", lambda: self.moveBlock("rotate"))
    
    def show(self): #shows and creates the block
        for i in self.cubes: #Deletes their placement from last frame (doesn't error if there is none)
            pen.delete(i)
        self.cubes = []
        #creates the four cubes that make up a block, depending on which type it is
        if self.type == 0: #Straight
            self.cubes = ["00", "10", "20", "30"]
        elif self.type == 1: #Backwards L
            self.cubes = ["00", "01", "11", "21"]
        elif self.type == 2: #Forwards L
            self.cubes =["01", "11", "21", "20"]
        elif self.type == 3: #Square
            self.cubes =["00", "01", "11", "10"]
        elif self.type == 4: #Rhombus 1 (Name ?)
            self.cubes =["01", "11", "10", "20"]
        elif self.type == 5: #T
            self.cubes =["01", "11", "21", "10"]
        elif self.type == 6: #Rhombus 2 (Name ?)
            self.cubes =["00", "10", "11", "21"]
        for i in range(0, 4): #Swaps out the coordinates for the four cubes with the objects at those positions
            tempX = int(self.cubes[0][0])
            tempY = int(self.cubes[0][1])
            self.cubes.append(tetrisCube(i, tempX, tempY, self.color, self.blockState, self.type, self.rotation, self.randID))
            self.cubes.pop(0)
        for i in self.cubes: #Draws the cubes
            i.drawCube()

    def moveBlock(self, direction): #Tells each cube to move down a square
        setTemp()
        global processingBlock, gameOn
        if gameOn:
            if processingBlock == False:
                processingBlock = True
                self.canMove = True #The block is free to move in the direction requested
                self.blockJustLanded = False #The block didn't just land on the ground or another block
                if self.blockState == 1: #Only checks to move blocks that are currently falling
                    if direction == "left":
                        for i in self.cubes: #Check to make sure each cube can safely move to its new position
                            i.checkSafetyLeft()
                            if not i.safeToMove:
                                self.canMove = False
                        if self.canMove: #If all cubes can safely move, moved them
                            for i in self.cubes:
                                i.shiftCube(-1, 0)
                    if direction == "right":
                        for i in self.cubes:
                            i.checkSafetyRight()
                            if not i.safeToMove:
                                self.canMove = False
                        if self.canMove:
                            for i in self.cubes:
                                    i.shiftCube(1, 0)
                    if direction == "down":
                        for i in self.cubes:
                            i.checkSafetyDown()
                            if not i.safeToMove:
                                self.canMove = False
                                i.state = 0
                                self.blockState = 0
                                self.blockJustLanded = True #The block will have just landed because it was 
                                                            #moving when the code was called but now it isn't    
                        if self.canMove:
                            for i in self.cubes:
                                i.shiftCube(0, 1)
                        elif self.blockJustLanded:
                            checkLine()
                            newBlock()
                    if direction == "rotate":
                        newRotation = []
                        for i in self.cubes:
                            i.safeToMove = True
                            self.tempX = 0
                            self.tempY = 0
                            newRotation.append(i.checkSafetyRotate())
                            if i.safeToMove == False:
                                self.canMove = False
                        if self.canMove:
                            for i in self.cubes:
                                i.rotateCube(newRotation, self.cubes.index(i))
                processingBlock = False

    def eraseCube(self, x):
        for i in self.cubes:
            i.eraseLine(x)

class tetrisCube: #The cells that make up each block
    def __init__(self, num, x, y, color, state, type, rotation, ID):
        global cubeList
        self.cubeNum = num
        self.x = x #x and y are for rotation only
        self.y = y
        self.type = type
        self.curXPos = 5 + x
        self.curYPos = 0 + y
        self.color = color
        self.state = state
        self.rotation = rotation
        self.randID = ID
        self.cubeJustLanded = False
        cubeList.append(f"{self.curXPos}:{self.curYPos}:{self.randID}")

    def checkSafetyRight(self):
        global gameOn, tempCubeList
        self.safeToMove = False
        if gameOn and self.state == 1 and not (self.curXPos + 1) > 13: #Game is on, the cube is falling, and the cube next door isn't a wall
            if not self.curXPos == 13:
                curID = f"{self.curXPos}:{self.curYPos + 1}:{self.randID}"
                if curID in tempCubeList: 
                    self.safeToMove = True
                else:
                    for i in tempCubeList:
                        if not f"{self.curXPos}:{self.curYPos + 1}:" in i:
                            self.safeToMove = True
    
    def checkSafetyLeft(self):
        global gameOn, tempCubeList
        self.safeToMove = False
        if gameOn and self.state == 1 and not (self.curXPos - 1) < 0:
            if not self.curXPos == 0:
                curID = f"{self.curXPos - 1}:{self.curYPos}:{self.randID}"
                if curID in tempCubeList: 
                    self.safeToMove = True
                else:
                    for i in tempCubeList:
                        if not f"{self.curXPos - 1}:{self.curYPos}:" in i:
                            self.safeToMove = True

    def checkSafetyDown(self):
        global gameOn, tempCubeList, cubeList
        self.safeToMove = True
        self.cubeJustLanded = False
        if gameOn and self.state == 1:
            if not (self.curYPos + 1) > 20:
                curID = f"{self.curXPos}:{self.curYPos + 1}:{self.randID}"
                if not curID in tempCubeList:
                    for i in tempCubeList:
                        if f"{self.curXPos}:{self.curYPos + 1}:".startswith(i):
                            print(f"Collion found at: {i} in {tempCubeList}. Main cube list is: {cubeList}")
                            self.safeToMove = False
                            if self.curYPos == 0: #If block is still at the top
                                print("GAME OVER")
                                gameOn = False
                                gameEnd()
                                master.destroy() #FIXME: Temporary end game
                            self.state = 0
                            self.cubeJustLanded = True
            else:
                self.safeToMove = False
                self.state = 0
                self.cubeJustLanded = True

    def checkSafetyRotate(self):
        global gameOn, tempCubeList
        touchingBorder = [((self.curXPos + 1) > 13), ((self.curXPos - 1) < 0), ((self.curYPos + 1) > 20), ((self.curYPos - 1) < 0)]
        if gameOn and self.state == 1 and not any(touchingBorder):
            tempX1 = self.x - 1
            tempY1 = self.y - 1
            tempX2 = -tempY1
            tempY2 = tempX1

            #The word "TEMP" is capitalized so I don't mix it for any other temporary variables 
            # (a lot are used here)
            TEMPcurXPos = self.curXPos - self.x
            TEMPcurYPos = self.curYPos - self.y
            TEMPx = tempX2 + 1
            TEMPy = tempY2 + 1
            TEMPcurXPos += TEMPx
            TEMPcurYPos += TEMPy
            
            curID = f"{TEMPcurXPos}:{TEMPcurYPos}:{self.randID}"
            if curID in tempCubeList:
                newRotation = [TEMPx, TEMPy, TEMPcurXPos, TEMPcurYPos]
                return newRotation
            else:
                for i in tempCubeList:
                    if f"{self.curXPos}:{self.curYPos}:" in i:
                        self.safeToMove = False
                        return False
                    else:
                        newRotation = [TEMPx, TEMPy, TEMPcurXPos, TEMPcurYPos]
                        return newRotation
        else:
            self.safeToMove = False
            return False

    def shiftCube(self, x, y): #Moves each cube to the right by one, shifting the whole block
        global cubeList
        cubeList.pop(cubeList.index(f"{self.curXPos}:{self.curYPos}:{self.randID}"))
        self.curXPos += x
        self.curYPos += y
        cubeList.append(f"{self.curXPos}:{self.curYPos}:{self.randID}")
        self.drawCube()

    def rotateCube(self, newRotation, cubeNum):
        global cubeList
        cubeList.pop(tempCubeList.index(f"{self.curXPos}:{self.curYPos}:{self.randID}"))
        self.x = newRotation[cubeNum][0]
        self.y = newRotation[cubeNum][1]
        self.curXPos = newRotation[cubeNum][2]
        self.curYPos = newRotation[cubeNum][3]
        cubeList.append(f"{self.curXPos}:{self.curYPos}:{self.randID}")

    def drawCube(self): #Draws the cube in its new position
        try: #Deletes old drawings if there were any
            pen.delete(self.cubeDrawn)
        except: #It errors if this except isn't here because it thinks the self.cubeDrawn line below is improperly indented
            if 1 == 2:
                print("Math broke")
        self.cubeDrawn = pen.create_rectangle(((cellSize * (self.curXPos)) + 11), ((cellSize * (self.curYPos)) + 60), ((cellSize * (self.curXPos)) + 11 + cellSize), ((cellSize * (self.curYPos)) + 60 + cellSize), fill=self.color, outline=colorLight, width=1)
    
    def eraseLine(self, x):
        global cubeList
        if self.curXPos == x:
            print("Erasing cube...")
            cubeList.pop(cubeList.index(f"{self.curXPos}:{self.curYPos}:{self.randID}"))
            pen.delete(self.cubeDrawn)
            self.cubeDrawn = 0

'''Functions'''
def checkered(canvas, lineDistance, lines): #draws lines
    #vertical lines, each lineDistance pixels apart
    for x in range(lineDistance, int(canvasWidth / 2), lineDistance):
        lines.append(canvas.create_line((x + 11), 60, (x + 11), (canvasHeight - 20), fill=colorLight))
    #horizontal lines, each lineDistance pixels apart
    for y in range(lineDistance, (canvasHeight - 60), lineDistance):
        lines.append(canvas.create_line(10, y + 60, (int(canvasWidth / 2) - 10), y + 60, fill=colorLight))

def setup():
    global upNextBox, board
    upNextBox = pen.create_rectangle((canvasWidth / 2) + 10, 60, canvasWidth - 10, canvasHeight - 100, fill=colorDark, outline=colorLight, width=3)
    board = pen.create_rectangle(10, 60, ((canvasWidth - 10) - (canvasWidth / 2)), canvasHeight - 20, fill=colorDark, outline=colorLight, width=3)
    checkered(pen, cellSize, gameLines)

def resumeGame(): #Start/stop loop
    global gameOn, coverUpNextBox, coverBoard, coverGameLines
    if gameOn: #if game is on; turns it off
        gameOn = False
        playPause["text"] = "Play"
        playPause["bg"] = "#7df585"
        playPause["fg"] = "#007a08"
        coverUpNextBox = pen.create_rectangle((canvasWidth / 2) + 10, 60, canvasWidth - 10, canvasHeight - 100, fill=colorDark, outline=colorLight, width=3)
        coverBoard = pen.create_rectangle(10, 60, ((canvasWidth - 10) - (canvasWidth / 2)), canvasHeight - 20, fill=colorDark, outline=colorLight, width=3)
        checkered(pen, cellSize, coverGameLines)
    else: #if game is off; turns it on
        playPause.place_forget()
        timeCount = 3
        countdown.place(x=(canvasWidth / 2) - 178, y=150)
        countdownUpdate(timeCount)

def countdownUpdate(t):
    global coverGameLines, gameOn
    if t > 0:
        countdown["text"] = t
        t -= 1
        master.after(1000, lambda: countdownUpdate(t))
    else:
        gameOn = True
        countdown.place_forget()
        playPause.place(x=((canvasWidth / 2) + 25), y=canvasHeight - 70)
        playPause["text"] = "Pause"
        playPause["bg"] = "#ff6b6b"
        playPause["fg"] = "#8f0000"
        pen.delete(coverUpNextBox)
        pen.delete(coverBoard)
        for i in coverGameLines:
            pen.delete(i)
        coverGameLines = []
        checkIfOn()

def gameEnd(): #FIXME: Doesn't delete
    global gameOn
    if gameOn: #Turns game off so it doesn't automatically start the next game
        resumeGame()
    for i in blocks:
        for j in i.cubes:
            pen.delete(j.cubeDrawn)
            del j
        del i
    print(blocks)

def checkLine(): #FIXME: Isn't clearing
    print("Checking line...")
    global cubeList
    lineCleared = True
    for i in range(0, 13):
        for j in range(0, 20):
            for k in cubeList:
                #print(k)
                if not f"{i}:{21 - j}:" in k:
                    lineCleared = False
        if lineCleared:
            print("Line full! Clearing line...")
            for i in range (0, 21):
                for k in blocks:
                    k.eraseCube(j)

def muteSound(): #Start/stop loop
    global sound, volumeButton
    if sound: #if game is on; turns it off
        sound = False
        volumeButton["text"] = "Unmute"
        volumeButton["bg"] = "#7df585"
        volumeButton["fg"] = "#007a08"
        pygame.mixer.music.stop()
    else: #if game is off; turns it on
        sound = True
        volumeButton["text"] = "Mute"
        volumeButton["bg"] = "#ff6b6b"
        volumeButton["fg"] = "#8f0000"
        pygame.mixer.music.play()

def setTemp(): #Sets the tempCubeList outside of the class so that it's global
    global cubeList, tempCubeList
    tempCubeList = cubeList

def updateLevel(x=1):
    global level, levelSlider
    level = levelSlider.get()
    levelDisplay["text"] = level
    levelDisplay.place_forget()
    levelDisplay.place(x=canvasWidth - (225 + (len(str(level)) * 8)), y=350)
    gameEnd() #Restarts level

def checkIfOn(): #Used to check if it should keep running
    global gameOn, level
    if gameOn:
        for i in blocks:
            if i.blockState == 1:
                i.moveBlock("down")
        master.after(int(1040 - (level * 40)), checkIfOn) #how long to wait before running the function again

def newBlock():
    global blocks, totalBlocks
    totalBlocks += 1
    blocks.append(tetrisBlock())
    blocks[len(blocks) - 1].show()

def options(): #opens options window; changes level and toggles sound
    global gameOn, level, levelSlider, volumeButton, sound
    if gameOn: #turns off the game so it isn't running while options are being adjusted
        resumeGame()
    #creates window
    optionsBox = Toplevel(bg=colorDark, bd=10)
    optionsBox.title("options")
    optionsBox.resizable(False, False) #disables resize screen
    optionsPen = Canvas(optionsBox, width=300, height=150, bg=colorDark, highlightbackground=colorDark)
    optionsPen.grid()

    '''labels'''
    optionsTitle = Label(optionsBox, text="Options", font = ("Unispace-Regular", 16), fg=colorMid, bg=colorDark)
    optionsTitle.place(x=5)
    optionsDesc = Label(optionsBox, text=f"Adjust the game options.", font = ("Unispace-Regular", 10), fg=colorMid, bg=colorDark, justify=LEFT)
    optionsDesc.place(x=5, y=30)

    levelLabel = Label(optionsBox, text="Level", font = ("Unispace-Regular", 12), fg=colorMid, bg=colorDark)
    levelLabel.place(x=5, y=65)
    levelSlider = Scale(optionsBox, variable=level, font=("Unispace-Regular", 12), length = 210, command=updateLevel, from_=1, to=25, orient=HORIZONTAL, bg=colorMid, fg=colorDark, bd=0, activebackground=colorLight, troughcolor=colorDark)
    levelSlider.place(x=75, y=59)
    levelSlider.set(level)

    volumeButton = Button(optionsBox, command=muteSound, font=("Unispace-Regular", 10), bd=0, padx=10, pady=5, activebackground="#5ee067", activeforeground="#005906", width=5)
    volumeButton.place(x=95, y=120)
    if sound:
        volumeButton["text"] = "Mute"
        volumeButton["bg"] = "#ff6b6b"
        volumeButton["fg"] = "#8f0000"
    else:
        volumeButton["text"] = "Unmute"
        volumeButton["bg"] = "#7df585"
        volumeButton["fg"] = "#007a08"

    closeoptions = Button(optionsBox, command=optionsBox.destroy, text="Close", font=("Unispace-Regular", 10), bd=0, bg="#7df585", padx=10, pady=5, fg="#007a08", activebackground="#5ee067", activeforeground="#005906", width=5) #"lambda" is used so that the function can be called with arguments
    closeoptions.place(x=200, y=120)

'''code'''
#create canvas
master = Tk() #create new window or "canvas" called "master"
master.title("Tetris") #window title
master.configure(bg = colorMid, bd=10)
master.resizable(False, False) #disables resize screen
pen = Canvas(master, width=canvasWidth, height=canvasHeight, bg=colorMid, highlightbackground=colorMid)
pen.pack()

#buttons
playPause = Button(master, command=resumeGame, text="Play", font=("Unispace-Regular", 10), bd=0, bg="#7df585", padx=15, pady=10, fg="#007a08", activebackground="#5ee067", activeforeground="#005906", width=5)
playPause.place(x=((canvasWidth / 2) + 25), y=canvasHeight - 70)
optionsButton = Button(master, command=options, text="Options", font=("Unispace-Regular", 10), bd=0, bg="#ffe770", padx=15, pady=10, fg="#877100", activebackground="#ffe359", activeforeground="#665500", width=5)
optionsButton.place(x=((canvasWidth / 2) + 115), y=canvasHeight - 70)
quitButton = Button(master, command=master.destroy, text="Quit", font=("Unispace-Regular", 10), bd=0, bg ="#ff6b6b", padx=15, pady=10, fg="#8f0000", activebackground="#ff3636", activeforeground="#690000", width=5)
quitButton.place(x=((canvasWidth / 2) + 205), y=canvasHeight - 70)
#labels/text in window
canvasTitle = Label(master, text="Tetris", font=("Unispace-Regular", 18), fg=colorLight, bg=colorMid)
canvasTitle.place(x=5) #pack has to be separate for some reason; else will break
version = Label(master, text="v.1.0 Feb. 2021", font=("Unispace-Regular", 8), anchor="center", fg=colorLight, bg=colorMid) #Version and date updated
version.place(x=102, y=12)
author = Label(master, text="By Raya Ronaghy", font=("Unispace-Regular", 8), anchor="center", fg=colorLight, bg=colorMid) #Author name
author.place(x=9, y=30)

upNext = Label(master, text="Next", font=("Unispace-Regular", 16), anchor="center", fg=colorLight, bg=colorDark) #Next label
upNext.place(x=canvasWidth - 180, y=80)
scoreButton = Label(master, text="Score", font=("Unispace-Regular", 16), anchor="center", fg=colorLight, bg=colorDark) #Score label
scoreButton.place(x=canvasWidth - 185, y=200)
levelButton = Label(master, text="Level", font=("Unispace-Regular", 16), anchor="center", fg=colorLight, bg=colorDark) #Levellabel
levelButton.place(x=canvasWidth - 255, y=300)
linesButton = Label(master, text="Lines", font=("Unispace-Regular", 16), anchor="center", fg=colorLight, bg=colorDark) #Lines label
linesButton.place(x=canvasWidth - 115, y=300)

scoreDisplay = Label(master, text=score, font=("Unispace-Regular", 20), anchor="center", fg=colorLight, bg=colorDark)
scoreDisplay.place(x=canvasWidth - (155 + (len(str(score)) * 8)), y=250)
levelDisplay = Label(master, text=level, font=("Unispace-Regular", 20), anchor="center", fg=colorLight, bg=colorDark)
levelDisplay.place(x=canvasWidth - (225 + (len(str(level)) * 8)), y=350)
linesDisplay = Label(master, text=lines, font=("Unispace-Regular", 20), anchor="center", fg=colorLight, bg=colorDark)
linesDisplay.place(x=canvasWidth - (85 + (len(str(lines)) * 8)), y=350)

countdown = Label(master, text="3", font=("Unispace-Regular", 60), anchor="center", fg=colorLight, bg=colorDark)

setup()

pygame.mixer.init() #enables music playing through pygame
pygame.mixer.music.load("Original Tetris Theme.mp3")
#pygame.mixer.music.play() FIXME: ENABLE THIS BEFORE FINISHING (Disabled so that music isn't distracting)

#Creates first block
blocks.append(tetrisBlock())
blocks[0].show()

resumeGame()

#FIXME: For debug, prints gameCubeList when 'p' pressed and totalBlocks when 't' pressed
def printGame():
    print(cubeList)
keyboard.add_hotkey("p", printGame)
def printNumBlocks():
    print(totalBlocks)
keyboard.add_hotkey("t", printNumBlocks)

mainloop() #is used for Tkinter