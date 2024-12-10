# Fumo Face Generator API

The API to generate the Fumo Face files.

## Usage
1. Clone the repository
2. Install the dependencies in `requirements.txt`
3. Run `fumo-face-generator.py`

## Genaration
To generate a face, it combines the DST files found in `face-parts`.
First it combines the eyes, then the eyebrows and lastly the mouth.
While the eyebrows and mouth are (almost) a simple copy and paste, the eye pasting has a bit more logic to it:

In order, it pastes:
1. The left pupil
2. The right pupil (color change if necessary)
3. The left & right eye shine (color change)
4. The left outline (color change)
5. The right outline (color change if necessary)
6. The top parts of the eyes (color change if necessary)

Where to jump after each part is dictated by the `positions.json` file in every `eyes/eye-(x)` folder,
which has the absolute X and Y coordinates for every eye part of that eye type.

`positions.json` should be generated in such a way that the lowest point of every eye coincides with `Y=-120`
