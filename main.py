import os
import subprocess
import json
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import threading as td
import tkinter.font as font
from tkinter.filedialog import askopenfilename
from scipy.stats import kde

import warnings
warnings.filterwarnings("ignore")

class Window():
    def __init__(self, master):
        self.replayName = ""
        self.processed = False
        self.font = font.Font(family="rlfont.ttf", size=25)
        self.fileInputLabel = tk.Label(master, text="Choose your replay file")
        self.fileInputLabel.config(font=self.font)
        self.fileInputLabel.pack()
        self.chooseReplayButton = tk.Button(master, text="Browse", command=self.browseReplay, height = 1, width = 10)
        self.chooseReplayButton["font"] = self.font
        self.chooseReplayButton.pack()
        self.loadDataButton = tk.Button(master, text="Load Data", command=self.loadDataThread, height = 1, width = 10, state="disabled")
        self.loadDataButton["font"] = self.font
        self.loadDataButton.pack()

        self.ballId = 0
        self.ids = {}
        self.posDict = {}
        self.playerDict = {}
        self.carDict = {}
        self.ballPosDict = {"X" : [], "Y": [], "Z": []}

        self.frame = tk.Frame(master, relief="ridge")

        self.playerChooseList = tk.Listbox(self.frame)
        self.playerChooseList.grid(row = 1, column = 2)

        self.playerHeatmapButton = tk.Button(self.frame, text = "Player HM", command = self.playerHeatmap, height = 1, width = 10)
        self.playerHeatmapButton["font"] = self.font
        self.playerHeatmapButton.grid(row = 2, column=2)

        self.allPlayerHeatmapButton = tk.Button(self.frame, text = "All player HM", command = self.allPlayerHeatmap, height = 1, width = 10)
        self.allPlayerHeatmapButton["font"] = self.font
        self.allPlayerHeatmapButton.grid(row = 3, column=1)

        self.ballHeatmapButton = tk.Button(self.frame, text = "Ball HM", command = self.ballHeatmap, height = 1, width = 10)
        self.ballHeatmapButton["font"] = self.font
        self.ballHeatmapButton.grid(row = 3, column=3)

        self.nbins = 50


    def browseReplay(self):
        self.frame.pack_forget()
        self.playerChooseList.delete(0, tk.END)
        self.ballId = 0
        self.ids = {}
        self.posDict = {}
        self.playerDict = {}
        self.carDict = {}
        self.ballPosDict = {"X" : [], "Y": [], "Z": []}
        self.loadDataButton["state"] = "disabled"

        tk.Tk().withdraw()
        self.replayName = r"{}".format(askopenfilename())
        if(not self.replayName.endswith(".replay") and self.replayName != ""):
            self.replayName = ""
            self.fileInputLabel["text"] = "File type not supported"
        else:
            thread = td.Thread(target=self.processFile)
            thread.start()

    def processFile(self):
        path = os.getcwd() + "/rlparser/RocketLeagueReplayParser.Console.exe "
        subprocess.call([path, self.replayName, "--fileoutput"])
        head, tail = os.path.split(self.replayName)
        try:
            os.remove("replay.json")
        except:
            pass
        os.rename(tail.rstrip(".replay") + ".json", "replay.json")
        self.processed = True
        self.loadDataButton["state"] = "normal"

    def loadDataThread(self):
        thread = td.Thread(target=self.loadData)
        thread.start()

        self.fileInputLabel["text"] = "Succesfully loaded data"
        self.frame.pack()

    def loadData(self):
        with open("replay.json") as f:
            data = json.load(f)

        frames = data["Frames"]
        actors = frames[0]["ActorUpdates"]

        for actor in actors:
            # get car ids with their actor ids
            if(actor["TypeName"] == "Archetypes.Car.Car_Default"):
                self.ids[actor["Engine.Pawn:PlayerReplicationInfo"]["ActorId"]] = actor["Id"]

            # get ball id
            elif(actor["TypeName"] == "Archetypes.Ball.Ball_Default"):
                self.ballId = actor["Id"]

            # connect player names with ids
            elif(actor["TypeName"] == "TAGame.Default__PRI_TA"):
                self.playerDict[actor["Id"]] = actor["Engine.PlayerReplicationInfo:PlayerName"]

        # get all positions of all players with actor["id"]
        for id in self.ids.values():
            self.posDict[id] = {"X" : [], "Y" : [], "Z" : []}

        # load players into list
        for idx, id in enumerate(self.ids):
            self.playerChooseList.insert(idx, self.playerDict[id])

        times = frames
        for time in times:
            for update in time["ActorUpdates"]:
                if update["Id"] in self.posDict.keys():
                    # associate both ids
                    try:
                        positionX = update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["X"]
                        positionY = update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["Y"]
                        positionZ = update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["Z"]
                        self.posDict[update["Id"]]["X"].append(positionX)
                        self.posDict[update["Id"]]["Y"].append(positionY)
                        self.posDict[update["Id"]]["Z"].append(positionZ)
                    except KeyError:
                        continue

                elif update["Id"] == self.ballId:
                    try:
                        self.ballPosDict["X"].append(update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["X"])
                        self.ballPosDict["Y"].append(update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["Y"])
                        self.ballPosDict["Z"].append(update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["Z"])
                    except KeyError:
                        continue

    def allPlayerHeatmap(self):
        allX = []
        allY = []

        for id in self.ids.values():
            allX += self.posDict[id]["X"]
            allY += self.posDict[id]["Y"]

        allX = np.array(allX)
        allY = np.array(allY)
        data = np.array([allX, allY])
        k = kde.gaussian_kde(data)
        xi, yi = np.mgrid[allX.min():allX.max():self.nbins*1j, allY.min():allY.max():self.nbins*1j]
        zi = k(np.vstack([xi.flatten(), yi.flatten()]))

        plt.figure()
        plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading="gouraud", cmap="magma")
        cb = plt.colorbar()
        cb.set_label("How often pos was droven on")
        plt.title("All players heatmap")
        plt.xlabel("x axis")
        plt.ylabel("y axis")

        plt.show()

    def ballHeatmap(self):

        allX = np.array(self.ballPosDict["X"])
        allY = np.array(self.ballPosDict["Y"])
        data = np.array([allX, allY])
        k = kde.gaussian_kde(data)
        xi, yi = np.mgrid[allX.min():allX.max():self.nbins*1j, allY.min():allY.max():self.nbins*1j]
        zi = k(np.vstack([xi.flatten(), yi.flatten()]))

        plt.figure()
        plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading="gouraud", cmap="magma")
        cb = plt.colorbar()
        cb.set_label("How often ball was on pos")
        plt.title("Ball heatmap")
        plt.xlabel("x axis")
        plt.ylabel("y axis")

        plt.show()

    def playerHeatmap(self):

        currentElement = self.playerChooseList.get(self.playerChooseList.curselection())

        # swap elements of dict for easier use
        tempDict = self.swapKeyValue(self.playerDict)

        currentPlayerId = tempDict[currentElement]
        currentCarId = self.ids[currentPlayerId]

        allX = np.array(self.posDict[currentCarId]["X"])
        allY = np.array(self.posDict[currentCarId]["Y"])
        data = np.array([allX, allY])
        k = kde.gaussian_kde(data)
        xi, yi = np.mgrid[allX.min():allX.max():self.nbins*1j, allY.min():allY.max():self.nbins*1j]
        zi = k(np.vstack([xi.flatten(), yi.flatten()]))

        plt.figure()
        plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading="gouraud", cmap="magma")
        cb = plt.colorbar()
        cb.set_label("How often pos was droven on")
        plt.title(currentElement + " heatmap")
        plt.xlabel("x axis")
        plt.ylabel("y axis")

        plt.show()

    def swapKeyValue(self, swapDict):
        new_dict = {}
        for k, v in swapDict.items():
            new_dict[v] = k

        return new_dict

    @classmethod
    def onclosing(self):
        try:
            os.remove("replay.json")
        except:
            pass

        root.destroy()
        os._exit(1)

root = tk.Tk()
root.geometry("600x600")
root.resizable(False, False)
root.title("RL Replay Stats")
window = Window(root)
root.protocol("WM_DELETE_WINDOW", Window.onclosing)
root.mainloop()
