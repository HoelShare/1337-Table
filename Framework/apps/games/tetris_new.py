from Framework.apps.games import Game
from random import randint
from Framework.theme import theme
import copy
import numpy as np
from Framework.font import render_text

class Block(object):
    name = "Block"
    rotationIndex = 0
    speed = 0.2
    shape = []
    xPos = yPos = 0

    def __init__(self, stage):
        self.stage = stage
        self.xPos = (stage.width - self.getWidth()) / 2

    def loop(self):
        pass

    def rotate(self):
        if self.canRotate() == False: return False
        self.shape = self.getRotationShape()
        return True

    def getRotationShape(self):
        return np.rot90(self.shape)

    def getShape(self):
        return self.shape

    def getWidth(self):
        return len(self.getShape())

    def getHeight(self):
        return len(self.getShape()[0])

    def canMove(self, x, y, shape=None):
        if shape is None: shape = self
        return self.stage.canMove(x, y, shape)

    def canRotate(self):
        rot = copy.deepcopy(self)
        rot.shape = rot.getRotationShape()
        return self.canMove(self.xPos, self.yPos, rot)

    def tryRotate(self):
        if self.canRotate():
            self.rotate()

    def moveRight(self):
        if self.canMove(self.xPos + 1, self.yPos):
            self.xPos = self.xPos + 1

    def moveLeft(self):
        if self.canMove(self.xPos - 1, self.yPos):
            self.xPos = self.xPos - 1

    def moveDown(self):
        if self.canMove(self.xPos, self.yPos + 1):
            self.yPos = self.yPos + 1
            return True
        return False

    def update(self, game, counter):
        if game.is_key_pressed("LEFT"):
            self.moveLeft()
        if game.is_key_pressed("RIGHT"):
            self.moveRight()
        if game.is_key_up("UP"):
            self.tryRotate()

        if (game.is_key_pressed("DOWN") or counter % 10 == 0) and self.moveDown() == False:
            self.stage.collectBlock(self)
            return True
        return False

    def draw(self, frame):
        for x in range(self.getWidth()):
            for y in range(self.getHeight()):
                shape = self.getShape()
                if shape[x][y] != 0:
                    dx = x + int(self.xPos) + self.stage.mapOffset[0]
                    dy = y + int(self.yPos) + self.stage.mapOffset[1]
                    frame[dy, dx] = self.color

    @staticmethod
    def createRandom(stage):
        blocks = [OBlock, TBlock, LBlock, IBlock, RevLBlock, RevSBlock, SBlock]
        i = randint(0, len(blocks) - 1)
        return blocks[i](stage)


class OBlock(Block):
    shape = [
        [1, 1],
        [1, 1]

    ]
    color = theme["tetris_1_color"]
    name = "o"

    def __init__(self, stage):
        super(OBlock, self).__init__(stage)


class IBlock(Block):
    shape = [
        [1],
        [1],
        [1],
        [1]
    ]
    color = theme["tetris_2_color"]
    name = "I"

    def __init__(self, stage):
        super(IBlock, self).__init__(stage)


class LBlock(Block):
    shape = [
        [1, 0],
        [1, 0],
        [1, 1]
    ]
    color = theme["tetris_3_color"]
    name = "L"

    def __init__(self, stage):
        super(LBlock, self).__init__(stage)


class RevLBlock(Block):
    shape = [
        [0, 1],
        [0, 1],
        [1, 1]
    ]
    color = theme["tetris_4_color"]
    name = "RevL"

    def __init__(self, stage):
        super(RevLBlock, self).__init__(stage)


class SBlock(Block):
    shape = [
        [0, 1, 1],
        [1, 1, 0]
    ]
    color = theme["tetris_5_color"]
    name = "S"

    def __init__(self, stage):
        super(SBlock, self).__init__(stage)


class RevSBlock(Block):
    shape = [
        [1, 1, 0],
        [0, 1, 1]
    ]
    color = theme["tetris_6_color"]
    name = "RevS"

    def __init__(self, stage):
        super(RevSBlock, self).__init__(stage)


class TBlock(Block):
    shape = [
        [0, 1, 0],
        [1, 1, 1]
    ]
    color = theme["tetris_7_color"]
    name = "T"

    def __init__(self, stage):
        super(TBlock, self).__init__(stage)


class Stage(object):
    width = 15
    height = 20
    mapOffset = (1, 0)
    isGame = True
    score = 0

    def __init__(self):
        self.world = [[0 for y in range(self.height)] for x in range(self.width)]

    def update(self):
        points = self.removeCompleteLines()
        self.score = self.score + points

    def removeCompleteLines(self):
        counter = 0
        for y in range(self.height):
            complete = True
            for x in range(self.width):
                if self.world[x][y] == 0:
                    complete = False
                    break
            if complete:
                counter = counter + 1
                self.removeLine(y)
        return counter

    def removeLine(self, yOffset):
        for y in range(yOffset, 0, -1):
            for x in range(self.width):
                self.world[x][y] = self.world[x][y - 1]

    def draw(self, frame, nextBlock):
        self.drawGame(frame, nextBlock)

    def drawGame(self, frame, nextBlock):
        self.drawBoard(frame, nextBlock)
        for x in range(self.width):
            for y in range(self.height):
                if self.world[x][y]:
                    dx = x + self.mapOffset[0]
                    dy = y + self.mapOffset[1]
                    frame[dy, dx] = self.world[x][y]

    def drawBoard(self, frame, nextBlock):
        for y in range(self.height):
            frame[y, self.mapOffset[0] - 1] = theme["tetris_borders"]
            frame[y, self.width + self.mapOffset[0]] = theme["tetris_borders"]

        render_text(frame, theme["text"], theme["tetris_background"], "%x" % self.score, self.width + self.mapOffset[0] + 2, 1)

        yOffset = 8
        xOffset = self.mapOffset[0] + self.width + 5
        for y in range(nextBlock.getHeight()):
            for x in range(nextBlock.getWidth()):
                shape = nextBlock.getShape()
                if shape[x][y] != 0:
                    frame[y+yOffset, x+xOffset] = nextBlock.color


    def canMove(self, xPos, yPos, block):
        isMoveable = self.checkBorder(block, xPos, yPos)
        return isMoveable and self.checkCollision(block, xPos, yPos)

    def checkBorder(self, block, xPos, yPos):
        if xPos < 0 or xPos + block.getWidth() > self.width:
            return False
        if yPos + block.getHeight() > self.height:
            return False
        return True

    def checkCollision(self, block, xPos, yPos):
        for x in range(block.getWidth()):
            for y in range(block.getHeight()):
                dx = x + xPos
                dy = y + yPos
                shape = block.getShape()
                if self.world[dx][dy] and shape[x][y] != 0:
                    return False
        return True

    def collectBlock(self, block):
        for x in range(block.getWidth()):
            for y in range(block.getHeight()):
                shape = block.getShape()
                if shape[x][y] != 0:
                    dx = x + block.xPos
                    dy = y + block.yPos
                    self.world[dx][dy] = block.color

    def endGame(self):
        self.isGame = False


class Tetris(Game):
    actualBlock = None
    nextBlock = None
    newBlock = True
    counter = 0

    def __init__(self, matrix, parent):
        super(Tetris, self).__init__(matrix, parent)
        self.stage = Stage()
        self.actualBlock = Block.createRandom(self.stage)
        self.nextBlock = Block.createRandom(self.stage)

    def loop(self):
        if self.stage.isGame:
            self.gameLoop()
        else:
            self.scoreBoardLoop()

        if self.is_key_down("B"):
            self.parent.back()

    def gameLoop(self):
        self.clear()
        if self.newBlock:
            self.actualBlock = self.nextBlock
            self.nextBlock = Block.createRandom(self.stage)
            self.counter = 0
        self.newBlock = self.actualBlock.update(self, self.counter)
        self.stage.update()
        if self.newBlock and self.counter == 0:
            self.stage.endGame()
        else:
            self.actualBlock.draw(self.frame)

        self.stage.draw(self.frame, self.nextBlock)
        self.counter = self.counter + 1

    def scoreBoardLoop(self):
        pass

if __name__ == "__main__":
    stage = Stage()
    #block = Block.createRandom(stage)
    print len(stage.world[0])