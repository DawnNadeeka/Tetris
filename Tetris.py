'''IMPORTS AND VARIABLES'''
import tkinter as tk
import keyboard #pip install keyboard
import pygame #pip3 install pygame
import random

#Game size
canvasHeight = 560
canvasWidth = 640
cellSize = 30
gameX = int((canvasWidth - 40) / (2 * cellSize))
gameY = int((canvasHeight - 80) / cellSize)

#Colors for the GUI
textColor = "#777777"
borderColor = "#222222"
bgColor = "#222222"
gameColor = "#333333"

score = 0
highscore = 0 #Just so the variable is defined
currentLevel = 1
totalLines = 0

gameOn = True
sound = True
optionsOpen = False
reset = False
checkNewBlock = False
blocks = [] #holds all of the tetrisBlock() objects
nextBlocks = []
cubeList = []
tempCubeList = []
processingBlock = False
blockBag = []
displayBag = []
blockColors = ["#55FFFF", "#5555FF", "#FFAA55", "#FFFF55", "#55FF55", "#AA55FF", "#FF5555"]
ghostColors = ["#385555", "#383855", "#554638", "#555538", "#385538", "#463855", "#553838"]
piecePos = [["00", "10", "20", "30"], #Cyan straight ("I")
["00", "01", "11", "21"], #Blue backwards L ("J")
["01", "11", "21", "20"], #Orange forwards L ("L")
["10", "11", "21", "20"], #Yellow square ("O")
["01", "11", "10", "20"], #Green rhombus 1 ("S")
["01", "11", "21", "10"], #Purple T ("T")
["00", "10", "11", "21"]] #Red rhombus 2 ("Z")

gameLines = [] #Holds the lines on the board
infoBox = 0
board = 0
nextUp = 0
coverGameLines = []
coverInfoBox = 0
coverBoard = 0
volumeButton = 0
levelSlider = 0

'''CLASSES'''
class tetrisBlock: #Creates a block
    def __init__(self):
        global blockBag
        self.type = blockBag[0]
        blockBag.pop(0)
        self.color = blockColors[self.type]
        self.cubes = [] #Holds all of the tetrisCube() objects
        self.blockState = 1 #0 = Resting, 1 = Falling, 2 = Being held (idk if I'll implement this one)
        self.randID = random.randint(100000, 999999) #A random id to identify this block from another
        self.rotation = 0
    
    def createBlock(self): #shows and creates the block
        global piecePos
        #creates the four cubes that make up a block, depending on which type it is
        self.cubes = piecePos[self.type].copy()
        for i in range(0, 4): #Swaps out the coordinates for the four cubes with the objects at those positions
            tempX = int(self.cubes[0][0])
            tempY = int(self.cubes[0][1])
            self.cubes.append(tetrisCube(i, tempX, tempY, self.color, self.blockState, self.type, self.rotation, self.randID))
            self.cubes.pop(0)
        for i in self.cubes: #Draws the cubes
            i.drawCube()
        self.ghost = ghostBlock(self.type, self.randID)

    def moveBlock(self, direction): #Checks to make sure the requested movement is "safe", or possible, 
                                    # before shifting each cube
        global processingBlock, gameOn, score, nextBlocks, checkNewBlock
        setTemp()
        if gameOn:
            if not processingBlock:
                processingBlock = True
                self.canMove = True #The block is free to move in the direction requested
                self.blockJustLanded = False #The block didn't just land on the ground or another block
                if self.blockState == 1: #Only checks to move blocks that are currently falling
                    if direction == "left":
                        for i in self.cubes: #Check to make sure each cube can safely move to its new position
                            i.checkSafetyLeft()
                            if not i.safeToMove:
                                self.canMove = False
                        if self.canMove: #If all cubes can safely move, move them
                            for i in self.cubes:
                                i.shiftCube(-1, 0)
                            self.ghost.moveBlock("left")
                    if direction == "right":
                        for i in self.cubes:
                            i.checkSafetyRight()
                            if not i.safeToMove:
                                self.canMove = False
                        if self.canMove:
                            for i in self.cubes:
                                i.shiftCube(1, 0)
                            self.ghost.moveBlock("right")
                    if direction == "down":
                        for i in self.cubes:
                            if not i.checkSafetyDown():
                                processingBlock = False
                                return
                            if not i.safeToMove:
                                self.canMove = False
                                i.state = 0
                                self.blockState = 0
                                self.blockJustLanded = True #The block will have just landed because it was 
                                                            #moving when the code was called but now it isn't    
                        if self.canMove:
                            score += 1
                            scoreNumber["text"] = score
                            scoreNumber.place_forget()
                            scoreNumber.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=250, anchor=tk.N)
                            for i in self.cubes:
                                i.shiftCube(0, 1)
                            self.ghost.moveBlock("down")
                        elif self.blockJustLanded:
                            checkLine()
                            self.ghost.eraseCube()
                            checkNewBlock = True
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
                            self.ghost.moveBlock("rotate")
                processingBlock = False

    def clearLineShift(self, linesCleared): #Tells each cube to move down a square
        for i in self.cubes:
            if i.curYPos < linesCleared:
                i.shiftCube(0, 1)

    def eraseCube(self, y):
        global score, totalLines
        copyCubes = self.cubes.copy()
        for i in self.cubes:
            if i.eraseLine(y):
                copyCubes.remove(i)
        self.cubes = copyCubes

class tetrisCube: #The cells that make up each block
    def __init__(self, num, x, y, color, state, type, rotation, ID):
        global cubeList, gameX
        self.cubeNum = num
        self.x = x #x and y are for rotation only
        self.y = y
        self.type = type
        self.curXPos = int(gameX / 2) - 2 + x
        self.curYPos = y
        self.color = color
        self.state = state
        self.rotation = rotation
        self.randID = ID
        self.cubeJustLanded = False
        self.cubeDrawn = 0
        cubeList.append(f"{self.curXPos}:{self.curYPos}:{self.randID}")

    def checkSafetyRight(self):
        global gameOn, tempCubeList, gameX
        self.safeToMove = False
        if gameOn and self.state == 1 and not (self.curXPos + 1) > (gameX - 1): #Game is on, the cube is falling, and the cube next door isn't a wall
            if not self.curXPos == (gameX - 1):
                curID = f"{self.curXPos + 1}:{self.curYPos}:{self.randID}"
                if curID in tempCubeList: 
                    self.safeToMove = True
                else:
                    tempSafeToMove = True
                    for i in tempCubeList:
                        if i.startswith(f"{self.curXPos + 1}:{self.curYPos}:"):
                            tempSafeToMove = False
                    if tempSafeToMove:
                        self.safeToMove = True
    
    def checkSafetyLeft(self): #Very similar to checkSafetyRight()
        global gameOn, tempCubeList
        self.safeToMove = False
        if gameOn and self.state == 1 and not (self.curXPos - 1) < 0:
            if not self.curXPos == 0:
                curID = f"{self.curXPos - 1}:{self.curYPos}:{self.randID}"
                if curID in tempCubeList: 
                    self.safeToMove = True
                else:
                    tempSafeToMove = True
                    for i in tempCubeList:
                        if i.startswith(f"{self.curXPos - 1}:{self.curYPos}:"):
                            tempSafeToMove = False
                    if tempSafeToMove:
                        self.safeToMove = True

    def checkSafetyDown(self):
        global gameOn, tempCubeList
        if gameOn and self.state == 1:
            self.safeToMove = True
            self.cubeJustLanded = False
            if not (self.curYPos + 1) > (gameY - 1):
                curID = f"{self.curXPos}:{self.curYPos + 1}:{self.randID}"
                if not curID in tempCubeList:
                    for i in tempCubeList:
                        if i.startswith(f"{self.curXPos}:{self.curYPos + 1}:"):
                            self.safeToMove = False
                            self.state = 0
                            self.cubeJustLanded = True
                            if self.curYPos < 2: #If block is still at the top
                                gameOn = False
                                gameEnd()
                                return False
            else:
                self.safeToMove = False
                self.state = 0
                self.cubeJustLanded = True
        return True

    def checkSafetyRotate(self):
        global gameOn, tempCubeList
        touchingBorder = [((self.curXPos + 1) > (gameX - 1)), ((self.curXPos - 1) < 0), ((self.curYPos + 1) > (gameY - 1)), ((self.curYPos - 1) < 0)]
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
                    if i.startswith(f"{self.curXPos}:{self.curYPos}:"):
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
        cubeList.remove(f"{self.curXPos}:{self.curYPos}:{self.randID}")
        self.curXPos += x
        self.curYPos += y
        cubeList.append(f"{self.curXPos}:{self.curYPos}:{self.randID}")
        self.drawCube()

    def rotateCube(self, newRotation, cubeNum):
        global cubeList
        cubeList.remove(f"{self.curXPos}:{self.curYPos}:{self.randID}")
        self.x = newRotation[cubeNum][0]
        self.y = newRotation[cubeNum][1]
        self.curXPos = newRotation[cubeNum][2]
        self.curYPos = newRotation[cubeNum][3]
        cubeList.append(f"{self.curXPos}:{self.curYPos}:{self.randID}")
        self.drawCube()

    def drawCube(self): #Draws the cube in its new position
        pen.delete(self.cubeDrawn) #Deletes old drawings if there were any
        self.cubeDrawn = pen.create_rectangle(((cellSize * (self.curXPos)) + 11), ((cellSize * (self.curYPos)) + 60), ((cellSize * (self.curXPos)) + 11 + cellSize), ((cellSize * (self.curYPos)) + 60 + cellSize), fill=self.color, outline=borderColor, width=1)
    
    def eraseLine(self, y): #Erases each cube on the line being cleared
        global cubeList
        if self.curYPos == y:
            cubeList.remove(f"{self.curXPos}:{self.curYPos}:{self.randID}")
            pen.delete(self.cubeDrawn)
            self.cubeDrawn = 0
            return True
        else:
            return False #cube was not removed because it's not on the x line that was cleared

class ghostBlock: #Creates a ghost block to show where the falling block will land
    def __init__(self, type, ID):
        global blockBag
        self.type = type
        self.color = ghostColors[self.type]
        self.borderColor = blockColors[self.type]
        self.cubes = [] #Holds all of the tetrisCube() objects
        self.rotation = 0
        self.randID = ID
        self.createBlock()
    
    def createBlock(self): #shows and creates the block
        global piecePos
        #creates the four cubes that make up a block, depending on which type it is
        self.cubes = piecePos[self.type].copy()
        for i in range(0, 4): #Swaps out the coordinates for the four cubes with the objects at those positions
            tempX = int(self.cubes[0][0])
            tempY = int(self.cubes[0][1])
            self.cubes.append(ghostCube(i, tempX, tempY, self.color, self.borderColor, self.type, self.rotation, self.randID))
            self.cubes.pop(0)
        for i in self.cubes: #Draws the cubes
            i.drawCube()
        self.moveBlock("down")

    def moveBlock(self, direction): #Moves ghost block
        self.canMove = True #The block is free to move in the direction requested
        if not direction == "down":
            for i in self.cubes: #Moves block up so it can detect the bottom correctly
                i.shiftCube(0, 0, True)
        if direction == "left":
            for i in self.cubes:
                i.shiftCube(-1, 0)
        elif direction == "right":
            for i in self.cubes:
                    i.shiftCube(1, 0)
        elif direction == "down":
            while self.canMove:
                for i in self.cubes:
                    i.checkSafetyDown()
                    if not i.safeToMove:
                        self.canMove = False
                        break
                if self.canMove:
                    for i in self.cubes:
                        i.shiftCube(0, 1)
            for i in self.cubes:
                i.drawCube()
        elif direction == "rotate":
            newRotation = []
            for i in self.cubes:
                self.tempX = 0
                self.tempY = 0
                newRotation.append(i.calcNewRotation())
                i.rotateCube(newRotation, self.cubes.index(i))
        if not direction == "down":
            self.moveBlock("down") #Moves block back down as far as it can

    def eraseCube(self):
        copyCubes = self.cubes.copy()
        for i in self.cubes:
            i.eraseLine()
            copyCubes.remove(i)
        self.cubes = copyCubes

class ghostCube: #The cells that make up each block
    def __init__(self, num, x, y, color, borderColor, type, rotation, ID):
        global cubeList, gameX
        self.cubeNum = num
        self.x = x #x and y are for rotation only
        self.y = y
        self.type = type
        self.curXPos = int(gameX / 2) - 2 + x
        self.curYPos = y
        self.color = color
        self.borderColor = borderColor
        self.rotation = rotation
        self.cubeDrawn = 0
        self.randID = ID

    def checkSafetyDown(self):
        global tempCubeList
        self.safeToMove = True
        if not (self.curYPos + 1) > (gameY - 1):
            curID = f"{self.curXPos}:{self.curYPos + 1}:{self.randID}"
            if not curID in tempCubeList:
                for i in tempCubeList:
                    if i.startswith(f"{self.curXPos}:{self.curYPos + 1}:"):
                        self.safeToMove = False
        else:
            self.safeToMove = False

    def calcNewRotation(self):
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
        
        newRotation = [TEMPx, TEMPy, TEMPcurXPos, TEMPcurYPos]
        return newRotation

    def shiftCube(self, x, y, top=False): #Moves each cube to the right by one, shifting the whole block
        if top:
            self.curYPos = self.y
        else:
            self.curXPos += x
            self.curYPos += y

    def rotateCube(self, newRotation, cubeNum):
        self.x = newRotation[cubeNum][0]
        self.y = newRotation[cubeNum][1]
        self.curXPos = newRotation[cubeNum][2]
        self.curYPos = newRotation[cubeNum][3]
        self.drawCube()

    def drawCube(self): #Draws the cube in its new position
        global blocks
        pen.delete(self.cubeDrawn) #Deletes old drawings if there were any
        self.cubeDrawn = pen.create_rectangle(((cellSize * (self.curXPos)) + 11), ((cellSize * (self.curYPos)) + 60), ((cellSize * (self.curXPos)) + 11 + cellSize), ((cellSize * (self.curYPos)) + 60 + cellSize), fill=self.color, outline=self.borderColor, width=1)
        for i in blocks:
            if i.blockState == 1:
                for j in i.cubes:
                    pen.tag_raise(j.cubeDrawn)

    def eraseLine(self): #Erases each cube on the line being cleared
        pen.delete(self.cubeDrawn)
        self.cubeDrawn = 0

class nextBlock: #Creates a block
    def __init__(self, num):
        global blockBag
        self.type = blockBag[num + 1]
        self.color = blockColors[self.type]
        self.cubes = [] #Holds all of the tetrisCube() objects
        self.position = num
    
    def createBlock(self): #shows and creates the block
        global piecePos
        #creates the four cubes that make up a block, depending on which type it is
        self.cubes = piecePos[self.type].copy()
        for i in range(0, 4): #Swaps out the coordinates for the four cubes with the objects at those positions
            tempX = int(self.cubes[0][0])
            tempY = int(self.cubes[0][1])
            self.cubes.append(nextCube(tempX, tempY, self.color, self.type, self.position))
            self.cubes.pop(0)
        for i in self.cubes: #Draws the cubes
            i.drawCube()

    def moveBlock(self): #Scoots blocks over
        global nextBlocks
        self.position -= 1
        for i in self.cubes:
            i.updatePos(self.position)
            i.drawCube()

    def eraseCube(self):
        copyCubes = self.cubes.copy()
        for i in self.cubes:
            i.eraseLine()
            copyCubes.remove(i)
        self.cubes = copyCubes
        nextBlocks.pop(0)

class nextCube: #The cells that make up each block
    def __init__(self, x, y, color, type, pos):
        self.x = x #x and y are for rotation only
        self.y = y
        self.type = type
        self.curXPos = x + (pos * 5)
        self.curYPos = y
        self.color = color
        self.cubeDrawn = 0
        self.position = pos

    def updatePos(self, pos):
        self.curXPos = self.x + (pos * 5)
        self.position = pos

    def drawCube(self): #Draws the cube in its new position
        global canvasWidth
        pen.delete(self.cubeDrawn) #Deletes old drawings if there were any
        #If statements are to make sure the long blue still fits on the screen right
        if self.type == 0 and not self.position == 0:
            self.cubeDrawn = pen.create_rectangle((((cellSize * (2 / 3)) * (self.curXPos)) + (canvasWidth / 2) + 18), (((cellSize * (2 / 3)) * (self.curYPos)) + 140), (((cellSize * (2 / 3)) * (self.curXPos)) + (canvasWidth / 2) + 18 + (cellSize * (2 / 3))), (((cellSize * (2 / 3)) * (self.curYPos)) + 140 + (cellSize * (2 / 3))), fill=self.color, outline=borderColor, width=1)
        elif self.type == 0 and self.position == 0:
            self.cubeDrawn = pen.create_rectangle((((cellSize * (2 / 3)) * (self.curXPos)) + (canvasWidth / 2) + 32), (((cellSize * (2 / 3)) * (self.curYPos)) + 140), (((cellSize * (2 / 3)) * (self.curXPos)) + (canvasWidth / 2) + 32 + (cellSize * (2 / 3))), (((cellSize * (2 / 3)) * (self.curYPos)) + 140 + (cellSize * (2 / 3))), fill=self.color, outline=borderColor, width=1)
        else:
            self.cubeDrawn = pen.create_rectangle((((cellSize * (2 / 3)) * (self.curXPos)) + (canvasWidth / 2) + 30), (((cellSize * (2 / 3)) * (self.curYPos)) + 140), (((cellSize * (2 / 3)) * (self.curXPos)) + (canvasWidth / 2) + 30 + (cellSize * (2 / 3))), (((cellSize * (2 / 3)) * (self.curYPos)) + 140 + (cellSize * (2 / 3))), fill=self.color, outline=borderColor, width=1)

    def eraseLine(self): #Erases each cube on the line being cleared
        global nextBlocks
        pen.delete(self.cubeDrawn)
        self.cubeDrawn = 0

'''FUNCTIONS'''
#Creating the game board
def setup(): #Creates game boxes
    global infoBox, board, highscore
    infoBox = pen.create_rectangle((canvasWidth / 2) + 10, 60, canvasWidth - 10, canvasHeight - 100, fill=gameColor, outline=borderColor, width=3)
    board = pen.create_rectangle(10, 60, ((canvasWidth - 10) - (canvasWidth / 2)), canvasHeight - 20, fill=gameColor, outline=borderColor, width=3)
    checkered(pen, cellSize, gameLines)

    #Sets highscore
    f = open("highscores.txt", "r")
    highscore = f.read()
    f.close()
    highscoreNumber["text"] = highscore
    highscoreNumber.place_forget()
    highscoreNumber.place(x=(((7 * canvasWidth) - 120) / 8) + 5, y=250, anchor=tk.N)

    #Enables music playing through pygame
    pygame.mixer.init()
    pygame.mixer.music.load("Original Tetris Theme.mp3")
    pygame.mixer.music.play()
    
    addBlocks(True)

    #Create blocks that display the next
    nextBlocks.append(nextBlock(0))
    nextBlocks.append(nextBlock(1))
    nextBlocks.append(nextBlock(2))
    for i in nextBlocks:
        i.createBlock()
    
    #Creates first block
    newBlock()

    #Hotkeys so that the game can react when these keys are pressed
    #keyboard.add_hotkey("left", lambda: detectMovement("left"))
    #keyboard.add_hotkey("right", lambda: detectMovement("right"))
    #keyboard.add_hotkey("down", lambda: detectMovement("down"))
    #keyboard.add_hotkey("up", lambda: detectMovement("rotate"))

    #Hotkeys for play/pause and muting the sound
    #keyboard.add_hotkey("space", resumeGame)
    #keyboard.add_hotkey("m", muteSound)

    master.bind("<Left>", lambda x: detectMovement("left"))
    master.bind("<Right>", lambda x: detectMovement("right"))
    master.bind("<Down>", lambda x: detectMovement("down"))
    master.bind("<Up>", lambda x: detectMovement("rotate"))
    
    #Hotkeys for play/pause and muting the sound
    master.bind("<space>", lambda x: resumeGame())
    master.bind("m", lambda x: muteSound())

def detectMovement(direction): #Figures out which blocks to move
    for i in blocks:
        if i.blockState == 1:
            i.moveBlock(direction)

def checkered(canvas, lineDistance, lines): #Draws lines
    #vertical lines, each lineDistance pixels apart
    for x in range(lineDistance, int(canvasWidth / 2), lineDistance):
        lines.append(canvas.create_line((x + 11), 60, (x + 11), (canvasHeight - 20), fill=borderColor))
    #horizontal lines, each lineDistance pixels apart
    for y in range(lineDistance, (canvasHeight - 60), lineDistance):
        lines.append(canvas.create_line(10, y + 60, (int(canvasWidth / 2) - 10), y + 60, fill=borderColor))

#Turning the game on and off
def resumeGame(): #Start/stop loop
    global gameOn, coverInfoBox, coverBoard, coverGameLines, reset, score, scoreNumber
    if gameOn: #if game is on; turns it off
        gameOn = False
        playPause["text"] = "Play"
        playPause["bg"] = "#7df585"
        playPause["fg"] = "#007a08"
        #Deletes old covers if there were any
        pen.delete(coverInfoBox)
        pen.delete(coverBoard)
        for i in coverGameLines:
            pen.delete(i)
        #Creates new covers
        coverInfoBox = pen.create_rectangle((canvasWidth / 2) + 20, 120, canvasWidth - 20, canvasHeight - 310, fill=gameColor, width=0)
        coverBoard = pen.create_rectangle(10, 60, ((canvasWidth - 10) - (canvasWidth / 2)), canvasHeight - 20, fill=gameColor, outline=borderColor, width=3)
        checkered(pen, cellSize, coverGameLines)
    else: #if game is off; turns it on
        playPause.place_forget()
        gameOver.place_forget()
        if reset:
            score = 0
            scoreNumber["text"] = score
            scoreNumber.place_forget()
            scoreNumber.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=250, anchor=tk.N)
            reset = False
        timeCount = 3
        countdown.place(x=((canvasWidth - 40) / 4), y=150, anchor=tk.N)
        countdownUpdate(timeCount)

def countdownUpdate(t): #Displays a short countdown before the game is resumed
    global coverGameLines, coverInfoBox, coverBoard, gameOn
    if t > 0:
        countdown["text"] = t
        t -= 1
        master.after(1000, lambda: countdownUpdate(t))
    else:
        gameOn = True
        countdown.place_forget()
        playPause.place(x=((canvasWidth / 2) + 20), y=canvasHeight - 90, anchor=tk.NW)
        playPause["text"] = "Pause"
        playPause["bg"] = "#ff6b6b"
        playPause["fg"] = "#8f0000"
        pen.delete(coverInfoBox)
        pen.delete(coverBoard)
        for i in coverGameLines:
            pen.delete(i)
        coverInfoBox = 0
        coverBoard = 0
        coverGameLines = []
        master.after(int(1040 - (currentLevel * 40)), checkIfOn)

def checkIfOn(): #Used to check if it should keep running
    global gameOn, currentLevel, blockBag, nextBlocks, checkNewBlock
    if gameOn:
        for i in blocks:
            if i.blockState == 1:
                i.moveBlock("down")
        if checkNewBlock:
            nextBlocks[0].eraseCube()
            for i in nextBlocks:
                i.moveBlock()
            nextBlocks.append(nextBlock(2))
            nextBlocks[2].createBlock()
            newBlock()
            checkNewBlock = False
        if len(blockBag) < 6:
            addBlocks()
        master.after(int(1040 - (currentLevel * 40)), checkIfOn) #how long to wait before running the function again

#Creating blocks
def addBlocks(starting=False):
    global blockBag, displayBag
    if starting: #The first piece should always be ("I, J, L, or T")
        tempBlockBag = [0, 1, 2, 5]
        random.shuffle(tempBlockBag)
        blockBag.append(tempBlockBag[0])
        tempBlockBag.pop(0)
        tempBlockBag.append(3)
        tempBlockBag.append(4)
        tempBlockBag.append(6)
        random.shuffle(tempBlockBag)
        for i in tempBlockBag:
            blockBag.append(i)
    else:
        tempBlockBag = []
        for i in range(0, 7):
            tempBlockBag.append(i)
        random.shuffle(tempBlockBag)
        for i in tempBlockBag:
            blockBag.append(i)
    
def newBlock():
    blocks.append(tetrisBlock())
    blocks[len(blocks) - 1].createBlock()

#Options box
def options(): #opens options window; changes level and toggles sound

    global gameOn, currentLevel, levelSlider, volumeButton, sound, optionsOpen
    optionsOpen = True
    if gameOn: #turns off the game so it isn't running while options are being adjusted
        resumeGame()
    #creates window
    optionsBox = tk.Toplevel(bg=bgColor, bd=10)
    optionsBox.title("options")
    optionsBox.resizable(False, False) #disables resize screen
    optionsPen = tk.Canvas(optionsBox, width=300, height=150, bg=bgColor, highlightbackground=bgColor)
    optionsPen.grid()

    #Labels
    optionsTitle = tk.Label(optionsBox, text="Options", font = ("Unispace-Regular", 16), fg=textColor, bg=bgColor)
    optionsTitle.place(x=5)
    optionsDesc = tk.Label(optionsBox, text=f"Adjust the game options.", font = ("Unispace-Regular", 10), fg=textColor, bg=bgColor, justify=tk.LEFT)
    optionsDesc.place(x=5, y=30)

    levelLabel = tk.Label(optionsBox, text="Level", font = ("Unispace-Regular", 12), fg=textColor, bg=bgColor)
    levelLabel.place(x=5, y=65)
    levelSlider = tk.Scale(optionsBox, variable=currentLevel, font=("Unispace-Regular", 12), length = 210, command=updateLevel, from_=1, to=25, orient=tk.HORIZONTAL, bg=bgColor, fg=textColor, bd=0, activebackground=textColor, troughcolor=textColor)
    levelSlider.place(x=75, y=59)
    levelSlider.set(currentLevel)

    volumeButton = tk.Button(optionsBox, command=muteSound, font=("Unispace-Regular", 10), bd=0, padx=10, pady=5, activebackground="#5ee067", activeforeground="#005906", width=5)
    volumeButton.place(x=75, y=120)
    if sound:
        volumeButton["text"] = "Mute"
        volumeButton["bg"] = "#ff6b6b"
        volumeButton["fg"] = "#8f0000"
    else:
        volumeButton["text"] = "Unmute"
        volumeButton["bg"] = "#7df585"
        volumeButton["fg"] = "#007a08"

    restartLevel = tk.Button(optionsBox, command=lambda: gameEnd(False), text="Restart", font=("Unispace-Regular", 10), bd=0, bg="#ffe770", padx=10, pady=5, fg="#877100", activebackground="#ffe359", activeforeground="#665500", width=5) #"lambda" is used so that the function can be called with arguments
    restartLevel.place(x=145, y=120)
    
    closeoptions = tk.Button(optionsBox, command=lambda: closeOptionsWindow(optionsBox), text="Close", font=("Unispace-Regular", 10), bd=0, bg="#7df585", padx=10, pady=5, fg="#007a08", activebackground="#5ee067", activeforeground="#005906", width=5) #"lambda" is used so that the function can be called with arguments
    closeoptions.place(x=220, y=120)

def closeOptionsWindow(optionsBox):
    global optionsOpen
    optionsOpen = False
    optionsBox.destroy()

def updateLevel(x=1): #Changes level display
    global currentLevel, levelSlider
    currentLevel = levelSlider.get()
    levelNumber["text"] = currentLevel
    levelNumber.place_forget()
    levelNumber.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=350, anchor=tk.N)
    gameEnd(False) #Restarts level

def muteSound(): #Start/stop loop
    global sound, volumeButton, optionsOpen
    if sound: #if sound is on; turns it off
        sound = False
        if optionsOpen:
            volumeButton["text"] = "Unmute"
            volumeButton["bg"] = "#7df585"
            volumeButton["fg"] = "#007a08"
        pygame.mixer.music.stop()
    else: #if sound is off; turns it on
        sound = True
        if optionsOpen:
            volumeButton["text"] = "Mute"
            volumeButton["bg"] = "#ff6b6b"
            volumeButton["fg"] = "#8f0000"
        pygame.mixer.music.play()

#Misc
def gameEnd(over=True): #Resets game
    global gameOn, blocks, score, highscore, nextBlocks, reset
    if gameOn: #Turns game off so it doesn't automatically start the next game
        resumeGame()
    tempBlocks = blocks.copy()
    for i in blocks:
        #Removes cubes
        tempCubes = i.cubes.copy()
        for j in i.cubes:
            pen.delete(j.cubeDrawn)
            tempCubes.remove(j)
            cubeList.remove(f"{j.curXPos}:{j.curYPos}:{j.randID}")
        i.cubes = tempCubes
        #Removes ghosts
        tempGhost = i.ghost.cubes.copy()
        for j in i.ghost.cubes:
            pen.delete(j.cubeDrawn)
            tempGhost.remove(j)
        i.ghost.cubes = tempGhost
        tempBlocks.remove(i)
    blocks = tempBlocks
    #Removes display blocks
    tempNextBlocks = nextBlocks.copy()
    for i in nextBlocks:
        tempDisplay = i.cubes.copy()
        for j in i.cubes:
            pen.delete(j.cubeDrawn)
            tempDisplay.remove(j)
        i.cubes = tempDisplay
        tempNextBlocks.remove(i)
    nextBlocks = tempNextBlocks

    addBlocks(True)
    nextBlocks.append(nextBlock(0))
    nextBlocks.append(nextBlock(1))
    nextBlocks.append(nextBlock(2))
    for i in nextBlocks:
        i.createBlock()
    newBlock()

    gameOn = True
    resumeGame()
    if over:
        gameOver.place(x=((canvasWidth - 40) / 4), y=150, anchor=tk.N)
        f = open("highscores.txt", "r")
        oldHighscore = f.read()
        f.close()
        if int(oldHighscore) < score:
            highscore = score
            highscoreNumber["text"] = highscore
            highscoreNumber.place_forget()
            highscoreNumber.place(x=(((7 * canvasWidth) - 120) / 8) + 5, y=250, anchor=tk.N)
            f = open("highscores.txt", "w")
            f.write(str(highscore))
            f.close()
        reset = True
    else:
        score = 0
        scoreNumber["text"] = score
        scoreNumber.place_forget()
        scoreNumber.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=250, anchor=tk.N)
    #Resets score and number of cleared lines
    totalLines = 0
    linesNumber["text"] = totalLines
    linesNumber.place_forget()
    linesNumber.place(x=(((7 * canvasWidth) - 120) / 8) + 5, y=350, anchor=tk.N)

def checkLine(): #Checks to see if any lines are full, and then clears them
    global cubeList, processingBlock, totalLines, gameX, gameY, currentLevel, score
    numLinesCleared = 0
    for i in range(0, gameY):
        lineCleared = True
        for j in range(0, gameX):
            cubeExists = False
            for k in cubeList:
                if k.startswith(f"{(gameX - 1) - j}:{i}:"):
                    cubeExists = True
            if not cubeExists:
                lineCleared = False
        if lineCleared:
            numLinesCleared += 1
            totalLines += 1
            linesNumber["text"] = totalLines
            linesNumber.place_forget()
            linesNumber.place(x=(((7 * canvasWidth) - 120) / 8) + 5, y=350, anchor=tk.N)
            lineHeight = i
            for k in blocks:
                k.eraseCube(i)
                if len(k.cubes) == 0:
                    del k
                else:
                    k.clearLineShift(lineHeight)
    if numLinesCleared == 1:
        score += 40 * currentLevel
    elif numLinesCleared == 2:
        score += 100 * currentLevel
    elif numLinesCleared == 3:
        score += 300 * currentLevel
    elif numLinesCleared == 4:
        score += 1200 * currentLevel
    scoreNumber["text"] = score
    scoreNumber.place_forget()
    scoreNumber.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=250, anchor=tk.N)

def setTemp(): #Sets the tempCubeList outside of the class so that it's global
    global cubeList, tempCubeList
    tempCubeList = cubeList.copy()

'''CODE'''
#Create canvas
master = tk.Tk() #create new window or "canvas" called "master"
master.title("Tetris") #window title
master.configure(bg = bgColor, bd=10)
master.resizable(False, False) #disables resize screen
pen = tk.Canvas(master, width=canvasWidth, height=canvasHeight, bg=bgColor, highlightbackground=bgColor)
pen.pack() #Pack/place has to be separate for some reason; else will break

#Buttons
playPause = tk.Button(master, command=resumeGame, text="Play", font=("Unispace-Regular", 10), bd=0, bg="#7df585", padx=15, pady=10, fg="#007a08", activebackground="#5ee067", activeforeground="#005906", width=5)
playPause.place(x=((canvasWidth / 2) + 20), y=canvasHeight - 90, anchor=tk.NW)
optionsButton = tk.Button(master, command=options, text="Options", font=("Unispace-Regular", 10), bd=0, bg="#ffe770", padx=15, pady=10, fg="#877100", activebackground="#ffe359", activeforeground="#665500", width=5)
optionsButton.place(x=(((3 * canvasWidth) - 40) / 4) + 10, y=canvasHeight - 90, anchor=tk.N)
quitButton = tk.Button(master, command=master.destroy, text="Quit", font=("Unispace-Regular", 10), bd=0, bg ="#ff6b6b", padx=15, pady=10, fg="#8f0000", activebackground="#ff3636", activeforeground="#690000", width=5)
quitButton.place(x=(canvasWidth - 20), y=canvasHeight - 90, anchor=tk.NE)

#Labels/text in window
canvasTitle = tk.Label(master, text="Tetris", font=("Unispace-Regular", 18), fg=textColor, bg=bgColor)
canvasTitle.place(x=5)
version = tk.Label(master, text="v.1.0 Feb. 2021", font=("Unispace-Regular", 8), anchor=tk.CENTER, fg=textColor, bg=bgColor) #Version and date updated
version.place(x=102, y=12)
author = tk.Label(master, text="By Raya Ronaghy", font=("Unispace-Regular", 8), anchor=tk.CENTER, fg=textColor, bg=bgColor) #Author name
author.place(x=9, y=30)

#Info box labels
upNext = tk.Label(master, text="Next", font=("Unispace-Regular", 16), fg=textColor, bg=gameColor) #Next label
upNext.place(x=(((3 * canvasWidth) - 40) / 4) + 10, y=80, anchor=tk.N)
scoreLabel = tk.Label(master, text="Score", font=("Unispace-Regular", 16), fg=textColor, bg=gameColor) #Score label
#scoreLabel.place(x=canvasWidth - 255, y=200)
scoreLabel.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=200, anchor=tk.N)
highscoreLabel = tk.Label(master, text="Highscore", font=("Unispace-Regular", 16), fg=textColor, bg=gameColor) #Score label
#highscoreLabel.place(x=canvasWidth - 140, y=200)
highscoreLabel.place(x=(((7 * canvasWidth) - 120) / 8) + 5, y=200, anchor=tk.N)
levelLabel = tk.Label(master, text="Level", font=("Unispace-Regular", 16), fg=textColor, bg=gameColor) #Levellabel
levelLabel.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=300, anchor=tk.N)
linesLabel = tk.Label(master, text="Lines", font=("Unispace-Regular", 16), fg=textColor, bg=gameColor) #Lines label
linesLabel.place(x=(((7 * canvasWidth) - 120) / 8) + 5, y=300, anchor=tk.N)

#Info box numbers
scoreNumber = tk.Label(master, text=score, font=("Unispace-Regular", 20), fg=textColor, bg=gameColor)
scoreNumber.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=250, anchor=tk.N)
highscoreNumber = tk.Label(master, text=score, font=("Unispace-Regular", 20), fg=textColor, bg=gameColor)
highscoreNumber.place(x=(((7 * canvasWidth) - 120) / 8) + 5, y=250, anchor=tk.N)
levelNumber = tk.Label(master, text=highscore, font=("Unispace-Regular", 20), fg=textColor, bg=gameColor)
levelNumber.place(x=(((5 * canvasWidth) - 40) / 8) + 15, y=350, anchor=tk.N)
linesNumber = tk.Label(master, text=totalLines, font=("Unispace-Regular", 20), fg=textColor, bg=gameColor)
linesNumber.place(x=(((7 * canvasWidth) - 120) / 8) + 5, y=350, anchor=tk.N)

#Status labels
countdown = tk.Label(master, text="3", font=("Unispace-Regular", 60), anchor=tk.CENTER, fg=textColor, bg=gameColor)
gameOver = tk.Label(master, text="GAME OVER", font=("Unispace-Regular", 20), anchor=tk.CENTER, fg=textColor, bg=gameColor)

setup()
resumeGame()
tk.mainloop() #is used for Tkinter
