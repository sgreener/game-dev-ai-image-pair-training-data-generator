from src.app import App

""" 
This is a tool to help produce training data 'pairs' (or more) for neural networks.
Mostly for my own use, but feel free to use it if you find it useful.

It takes groups of source images, and generates a set of tiles from each source image.
It can also apply random transformations to the images, such as rotation and flipping, to increase the diversity of the training data.
 
Note: This is an app thats been created using using Gemini 2.5 using co pilot.
"""

if __name__ == '__main__':
    app = App()
    app.MainLoop()
