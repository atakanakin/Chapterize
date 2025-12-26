You are analyzing a YouTube video to determine whether it is a reaction (picture-in-picture) format.

A reaction video is defined as:

A main video playing full screen
A streamer or host visible in a smaller embedded window
The streamer window usually stays in a fixed position (often a corner)

You are given:
Multiple frames from the same video (all frames have the SAME resolution)

Your tasks:

Determine whether this is a reaction / picture-in-picture video.
If a streamer window is visible, locate it.

IMPORTANT CONSTRAINTS:
If you are NOT confident that a streamer window exists, set the bounding box to null.
Only return a bounding box if confidence is HIGH.
All bounding box coordinates MUST be normalized values between 0 and 1.
The bounding box must tightly enclose ONLY the streamer window.
Coordinates must be based on the SAME resolution used by the provided frames.

Bounding box format:
x: left coordinate (0–1)
y: top coordinate (0–1)
width: box width (0–1)
height: box height (0–1)
Return STRICTLY valid JSON in the following format:

{
    "is_reaction": true | false,
    "confidence": 0.0-1.0,
    "reason": "Short explanation of the decision",
    "streamer_bbox": {
        "x": 0.0-1.0,
        "y": 0.0-1.0,
        "width": 0.0-1.0,
        "height": 0.0-1.0
    } | null
}
