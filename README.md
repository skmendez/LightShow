# RGB Music Visualizer
## What is it?
The goal of this project is to efficiently display music videos of whatever song is playing on the keys of my RGB Keyboard, the K95 RGB.

## How does it work?
My beginning tests started with constant screenshots of the monitor being taken, which were subsequently resized and then the average color from the swatches which were over the top of a given key was assigned to that color.

This has one clear disadvantage; to have a music video display, you have to be watching it on one monitor.
I'm currently developing the solution, but requires a lot of gears to operate well.

## Processing Steps
1. First, we continuously poll the name of the Spotify window and the Chrome window to see if a music video pops up. For Chrome, this does require having the music video as the active tab of the window, which I'm not sure of a workaround for.

2. Once it's determined that a song is playing, we check to see if we've already processed the song, in which case we skip step 3. Otherwise, we must find the video on YouTube and download it to start processing.

3. Once the video is downloaded, it must be processed. Processing of the video involves stepping through the video at a given FPS and creating a row in an array for every frame which states the RGB values of every single key for the given frame.
This ndarray is saved in npz format, along with the wav file of the video and the fps at which the video was played.

4. Now, we must sync the music playing through the speakers with the demo file for the keys. We do this by correlating ~4 seconds of the currently playing audio with the wav file to find the location into the song in seconds.

5. Once we have this, we just start playing the demo file at that point in time, which actually syncs up very well right now.

## Improvements Needed

It would be nice if the demo pauses when the music is paused. Also, it only really works as a one-off thing, so continuous playing support would also be great.

## Dependencies

Dependencies are listed in `requirements.txt`. Of note is that a special version of PyAudio with loopback must be used, found [here](https://github.com/intxcc/pyaudio_portaudio)
