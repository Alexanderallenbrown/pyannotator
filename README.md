# pyannotator

This is a simple tool for coding video of fish (or anything else, really) that saves text files for post-processing. It also saves "positive" samples of the thing you're tracking and "negative" samples into the same directory 
as your video, so that you can use these samples to train a machine learning algorithm. If you are working with a more advanced algorithm like R-CNN, it also saves full frames from the video along with an annotations file that contains bounding box
information for all objects you tracked.

# Installation Instructions:

go to home directory (or anywhere) in terminal, and type:
```
$git clone https://github.com/Alexanderallenbrown/pyannotator
```
Then change directories into the pyannotator folder:
``` $cd pyannotator```

Then, run the program:

```$python annotator.py```

# How to use pyAnnotator:

once it opens, here is how to use it:

* enter number of fish in the video you're going to track
* enter how many frames you'd like to skip at once (I use 10)
* click the button to select a video file
* click the button to start tracking
* drag top left to bottom right around first fish
* hit space bar
* repeat for each fish
* once the frame number increments to the next frame, hit 'm' to change to a simple click rather than having to drag the bounding box. Now, you can just slide the bounding box for each fish around. much quicker.
* because this will be used for training CV algorithms, I have to know whether the fish is occluded (blocked by something). To mark a fish as occluded, hit 'o' before hitting space bar to advance to the next fish.
*when you're done, or when the video is over, hit 'q', then close the GUI window (not the openCV window) to exit.
