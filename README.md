# Fumo Face Generator API

The API to generate the Fumo face files. You can run it as a web server or as a CLI tool.

## Usage
1. Clone the repository: `git clone https://github.com/SartoRiccardo/fumo-face-maker-api.git && cd fumo-face-maker-api`
2. Install the dependencies: `pip install -r requirements.txt`
3. You can now either run the web server or the CLI tool.
   - To run the web server, simply run `fumo-face-maker.py`
   - To run it as a CLI tool, run `generator.py` as an executable on your terminal


## Genaration
To generate a face, it combines the DST files found in `face-parts`.
First it combines the eyes, then the eyebrows and lastly the mouth.
While the eyebrows and mouth are (almost) a simple copy and paste, the eye pasting has a bit more logic to it:

In order, it pastes:
1. The left pupil
2. The right pupil (color change if necessary)
    - Should the left and right pupil have different colors (e.g. gradient eyes), it will switch between pasting the left and the right after each color change.
3. The left & right eye shine (color change)
4. The left outline (color change)
5. The right outline (color change if necessary)
6. The top parts of the eyes (color change if necessary)

Where to jump after each part is dictated by the `positions.json` file in every `eyes/eye-(x)` folder,
which has the absolute X and Y coordinates for every eye part of that eye type.

`positions.json` should be generated in such a way that the lowest point of every eye coincides with `Y=-120`
