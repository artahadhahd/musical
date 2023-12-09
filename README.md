# Instructions to Download

## Via GitHub
Scroll up, click on `Code` and select `Download ZIP`.
Unzip the file, and you're good to go!

You can now skip to [the instructions](#instructions-for-using-musical).


## Via Git
- Download Git from [here](https://git-scm.com/downloads)
- Open a terminal and run the following command:
```
git clone https://github.com/artahadhahd/musical
```
- Then run this command:
```
cd musical
```

# Instructions for using `musical`
For now, you can't import other files into your project.
Open `test.musical` and [start writing](#syntax)

Then, run the `run.sh` file. Make sure that you have [FFMPEG](https://ffmpeg.org/download.html) (required for compiling to a `wav` file) and the latest version of [Python](https://www.python.org/downloads/) installed on your machine.

# Syntax

**Make sure that there's always a new line at the end of your file.**

## Header basics
Every program has a header. You have to give at least a meter or a BPM. There are other keys that you can define, but they are not necessary as they are assigned to a default value.
Example:
```
meter: 4/4
bpm: 60

```

## Functions
Functions start with `@`. A `main` function is required in all programs. A function can be empty. Two functions with the same name cannot be defined.

```
@main
save main.bin

```

In order to call a function, you use the `goto` keyword.

```
@main
goto intro
save main.bin

@intro
A 1/2

```

The order of the functions doesn't matter, you can write them anywhere inside the file. So this is the same as above:
```
@intro
A 1/2

@main
goto intro
save main.bin

```

# Variables
Variables are defined like this:
```
variable_name: value

```

For example:

```
@main
octave: 5
A   1
octave: 4
A   1
pitch: 415
A   1
save main.bin

```

# If statements (Control Flow)
Not implemented yet, no need for them for now.

# Loops
Coming soon.

# Features planned:
ADSR, Chords

But this project is gonna be retired soon, and it will be replaced by a more modern one with way more capabilities.