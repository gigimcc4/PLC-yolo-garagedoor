# plate video for the dock door (simulated)

a fake dock camera at door 1. one vehicle at a time drives up, stops with the front plate in view, then pulls off to the left.
16 vehicles, 4.5 s each, 72 s total, 1920x1080 at 30 fps. made with HyperFrames (html rendered to video).

the plates come from the `truck_id` column of the schedule that `dock_shipments.ipynb` makes (`seed=42`), plus vehicles that should be turned away.

## files

- `dock_cam_plates.mp4` the video
- `ground_truth.csv` the answer key: one row per vehicle with its time window, frames, plate text, whether it's on the manifest, and what the door should do
- `lineup.json` the list of vehicles. edit this to change plates or add vehicles
- `build.py` turns lineup.json into index.html and ground_truth.csv
- `index.html` the HyperFrames composition

## what's in it

- 7 trucks on the manifest (should open)
- 5 vehicles that aren't trucks or aren't on it: car, pickup, 2 buses, TRL-000
- 3 near misses: TRL-I95 (letter I), TRL-528 (one digit off), TRL-44B (letter B)
- TRL-125: on the manifest but already marked arrived, so `find_truck()` says no. it opens if you reset the day (step 9) first
- a few harder ones: angled approach, and TRL-928 in dim light with a dirty plate

`plate_clear_from_s` to `plate_clear_to_s` is when the vehicle is stopped and the plate is easiest to read.

## change it

```
python3 build.py
npx hyperframes render --output dock_cam_plates.mp4
```

needs node 22+ and ffmpeg.
