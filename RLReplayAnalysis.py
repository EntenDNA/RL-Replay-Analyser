import json
import matplotlib.pyplot as plt
import numpy as np

with open('replay.json') as f:
  data = json.load(f)

  # connect player with car
ids = []
frames = data["Frames"]
actors = frames[0]["ActorUpdates"]
for actor in actors:
    if(actor["TypeName"] == "Archetypes.Car.Car_Default"):
        ids.append({actor["Id"] : actor["Engine.Pawn:PlayerReplicationInfo"]["ActorId"]})

# get all positions of all players with actor["id"]
posDict = {}
for id in ids:
    for key in id:
        posDict[key] = {"X" : [], "Y" : [], "Z" : []}

times = frames[1:]
for time in times:
    for update in time["ActorUpdates"]:
        if update["Id"] in posDict.keys():
            try:
                positionX = update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["X"]
                positionY = update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["Y"]
                positionZ = update["TAGame.RBActor_TA:ReplicatedRBState"]["Position"]["Z"]
                posDict[update["Id"]]["X"].append(positionX)
                posDict[update["Id"]]["Y"].append(positionY)
                posDict[update["Id"]]["Z"].append(positionZ)
            except KeyError:
                continue

# 3d lineplot
"""
ax = plt.axes(projection="3d")

for dit in ids:
    for id in dit:
        print(id)
        ax.plot3D(np.array(posDict[id]["X"]), np.array(posDict[id]["Y"]), np.array(posDict[id]["Z"]))
"""


# 2d heatmap for one player

"""
plt.hist2d(np.array(posDict[8]["X"]), np.array(posDict[8]["Y"]), bins=50, normed=False, cmap='plasma')
cb = plt.colorbar()
cb.set_label('How often pos was droven on')
plt.title('Heatmap of 2D normally distributed data points')
plt.xlabel('x axis')
plt.ylabel('y axis')
"""

# 2d heatmap for all players
"""
allX = []
allY = []

for dit in ids:
    for id in dit:
        allX += posDict[id]["X"]
        allY += posDict[id]["Y"]

plt.hist2d(np.array(allX), np.array(allY), bins=50, normed=False, cmap='plasma')
cb = plt.colorbar()
cb.set_label('How often pos was droven on')
plt.title('Heatmap of 2D normally distributed data points')
plt.xlabel('x axis')
plt.ylabel('y axis')
"""

plt.show()
