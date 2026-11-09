# Marker cube mount: first-print check list

For Emily Simpson (3D print) and the team (bench test). Ben Zheng, 2026-11-09. Plain language on purpose.
The goal is one printed part per probe (clip + stalk + cube), two copies each. Print one first, test it with
this list, then print the other three.

## Before printing

- [ ] Handle width and thickness measured on the real probe at the clip zone (100 to 130 mm above the probe
      face) and typed into the CAD file. The numbers in the file are estimates from a photo, about plus or
      minus 3 mm. On the L4-12t-RS the clip must sit above the two buttons.
- [ ] Stalk leans forward, over the patient, never towards the cable and the operator's wrist. Lean about
      25 degrees. If more tilt clearance is needed make it more upright; a longer stalk does not help.
- [ ] Clamp style chosen. Two-piece clamp with M3 screws is the safe choice. A snap-fit C-clip is quicker but
      the opening has to be nearly as wide as the handle, so it holds less firmly and PLA may crack when flexed.
- [ ] Filament: white, matte. Not glossy, not grey, not "natural" translucent.
- [ ] Print settings: 0.2 mm layers or finer, 3 perimeters, 4 or more top layers, 10 to 15 percent infill.
      The cube is drawn solid so the slicer can hollow it.
- [ ] Orientation: no supports touching any of the five marker faces. The bottom face of the cube (where the
      stalk joins) and the clip can carry supports or sit on the bed.

## When the part comes off the printer

1. **Flat faces.** Lay a steel ruler across each marker face. No daylight under it bigger than a sheet of paper
   (about 0.1 mm). Warped or bumpy faces make the tracker read the wrong angle.
2. **Recess.** A 51 mm sticker drops in and sits flush, not proud of the rim. If it is tight, the recess can
   grow by 0.5 mm. If it rattles, fine, the glue fixes it.
3. **Labels readable.** Face numbers 1 to 5 and the up-arrows can be read by eye. They tell us which marker
   went where.
4. **Fit on the probe.** With 1 mm foam tape inside, the clip closes on the handle and the probe can be shaken
   without the clip rotating or sliding. Buttons and cable are free. A normal scanning grip does not touch the
   clip or stalk, and the cable drapes back over the wrist without touching the stalk.
5. **Stiffness.** Push the cube sideways with a finger. It should flex less than a millimetre and spring back.
6. **Weight.** The part should weigh under about 80 g. The probe should not feel top-heavy in the hand.

## On the bench (team, 20 minutes)

7. **Stickers on.** Print the marker sheet at 100 percent, measure a marker (35 mm), cut on the grey line,
   glue one per face. Write down which marker id went on which face number. Photograph the cube.
8. **Camera view.** Phone on the tripod about 30 cm away on the far side of the patient, looking down at
   45 degrees towards the operator. In the normal grip the top face and the front face are both fully visible.
9. **Tilt clearance.** On the phantom, tilt the probe 45 degrees towards the cube side. The cube should stay
   about 7 cm above the surface (design value 74 mm; at 60 degrees about 24 mm remain). Nothing touches.
10. **Tracking.** Record a practice sweep. The tracker should find the cube in at least 95 percent of frames
   and the still probe should jitter by less than 1 mm. (2026-10-30 with the paper cube: 87 to 97 percent,
   0.2 to 0.5 mm.)
11. **Numbers recorded.** Cube edge, marker edge, cube centre to probe face (from the CAD plus the measured clip
    height on the probe), marker-to-face map. These go into the layout file; nothing works without them.

## If something fails

| Problem | Likely cause | Fix |
| --- | --- | --- |
| Clip loose or rotates | handle measured small, or corners rounder than modelled | reduce `foam` or `handle_w`/`handle_t` by 1 mm, thicker foam, reprint only the clip if it is a separate part |
| Clip will not close | handle measured large | add 1 mm to `handle_w`/`handle_t` |
| Face not flat | printed with supports on it, or top layers too few | reorient, more top layers, print cooler |
| Sticker proud of the rim | recess too shallow for the paper | `recess_depth` 0.7 |
| Cube reaches the surface on a forward tilt | stalk leans too far forward | `stalk_lean` 20 (more upright); a longer stalk does not help |
| Cube hides behind the hand on camera | camera too low or too far to the side | raise the phone, move it to face the operator |
| Tracker loses the cube when the probe tilts | only one face visible | move the phone further behind the probe |

## After a pass

Print the remaining three (one more for this probe, two for the other probe with its own handle numbers).
Keep the first print as the spare.
