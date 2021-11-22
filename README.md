# PRIMA

### Project to simulate PRIMA bionic vision system for CS291A Fall 2021 and beyond
### Team : Apurv, Avani, Byron, Shravan









#### References and Notes
A way to connect Unity and Python - 
use this repo to set it up - use the Unity project in here
https://github.com/off99555/Unity3D-Python-Communication
change the server.py and Client.cs (HelloClient.cs in this case) files according to the repo below 
https://vinnik-dmitry07.medium.com/a-python-unity-interface-with-zeromq-12720d6b7288
https://github.com/vinnik-dmitry07/PythonUnityInterface/blob/main/UnityProject/Assets/Scripts/Data.cs

-> Our first idea is to connect Unity and Python and show p2p percept of a single Landolt C - an image that the server sends to the client (client first sends a raw image/empty frame) that then gets displayed on Unity
-> We are able to achieve this but it hangs - known bug for using ZeroMQ
