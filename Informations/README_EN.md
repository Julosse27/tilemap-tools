# Tilemap Tools

<font size=4> Python tool to facilitate the use of templates with the `pyxel` module. </font>

---
## Installation
```bash
pip install tilemap-tools
```

----
## Features

<font size=3>

 - ✨ Create interactive pixel art tilemap templates.
 - 🎨 Palettes of up to 32 colors per template.
 - 👁️ Visualization and modification with interactive grids.
 - 💻 Modification at any time
 - 👾 Tilemap creation with a complete system for creating platforms or third-party models.
 - 👨‍💻 Easy to use in a program using the pyxel module ([documentation](https://kitao.github.io/pyxel/web/user-guide/))

 </font>

-------
## Usage

### **Creating a file**
The `tilemap create` command allows you to create the files needed to use this module.

### Template file
The template file (`.mdl`) is created with the `tilemap create modele` command and will be used to create a tilemap file (`.map`).

It will contain a set of tiles made up of a maximum of 32 different colors.

If no colors are provided, some basic colors will be available.

#### Arguments
This command requires 2 mandatory arguments:
- The `taille` argument: number of pixels on each side of each tile (maximum is 32 pixels).

- The `output` argument: The path where the file will be saved. Can be absolute or relative.

But it also has several optional arguments:
- The `--nb-tuiles` (or `-n`) argument: the number of tiles that the file will contain. This will allow more choices when creating a tilemap file with this file.

- And finally, the `--couleurs` (or `-c`) argument: To build this template you can use any color, this is where you must specify which ones. After mentioning this argument you must specify one or more hexadecimal codes corresponding to the colors you want to use. You can use from 1 to 32 different colors for a single template!!!

#### Examples
```bash
tilemap create modele 9 my_template.mdl -c FF0000 00FF00 0000FF

tilemap create modele 12 my_custom_template.mdl -n 4
```

For more help:
```bash
tilemap create modele -h
```

### Tilemap file
A tilemap file (`.map`) is the file that will allow you to include your creations in your program. This file will combine the tiles from one or more template files (`.mdl`) with the only limit being a 512-pixel square to fill with your creations.

#### Arguments
This command has 2 mandatory arguments:
- The `output` argument: the name of the file to be created ( /!\ Don't forget the extension /!\ ). You can specify this path as relative or absolute.

- The `modeles` argument: these are the names of the template files (`.mdl`) you have used. You can specify them as relative or absolute paths.

#### Example

```bash
tilemap create map tilemap.map template1.mdl template2.mdl template3.mdl
```

For more help:
```bash
tilemap create map -h
```

### **Viewing a template or tilemap**
After creating your template for your future game or other project, you can view it with this simple command.
```bash
tilemap view path_to_tilemap.map
# or
tilemap view path_to_template.mdl
```

### **Clearing temporary files**
As this module is still in development, I'm making this command available to delete temporary files that might not be deleted in case of potential errors or program interruptions.
```bash
tilemap clear
```

## **Integration in a program**

### **The `~.Modele` and `~.Tilemap` objects**
After creating files, you need to be able to modify them. This is what these 2 objects are for, allowing you to create a link between the file you just created and your program.

As long as you know the path to your file, you only need one line to create one:
```python
from tilemap_tools import Modele, Tilemap

modele = Modele("C:\\path\\to\\your\\file.mdl")

tilemap = Tilemap("my_file.map")
```

You can directly create a new file with `Modele.create` or `Tilemap.create`.

```python
from tilemap_tools import Modele, Tilemap

# To create a new template
modele = Modele.create(taille=3, nb_tiles=3, couleurs=["ffffff", "f33aaa"])
# or to create a new tilemap file
tilemap = Tilemap.create("my_file.mdl", modele)
```

But you can also modify or view them directly in your program.
```python
from tilemap_tools import Modele

modele = Modele("my_template.mdl")

# To modify this file call:
modele.modif()
# or to see its content:
modele.view()
# of course this works the same way for the tilemap object
```

### **The `~.Element` object**
The first part of the integration was focused on recreating what this module already did in a Python program.

This second part implements a complete system to be able to display what you just created and animate it in a program with `pyxel`

You can create it in 2 ways:
```python
from tilemap_tools import Tilemap, Element

# First, in any case, you need to create a link
# with a tilemap file (to get the template)
tilemap = Tilemap("my_tilemap_file.map")

# Then either you use the Tilemap.create_element method
element1 = tilemap.create_element(
    10, 10, # The x-y coordinates where it should be displayed.
    9, 12, # The size (width then height) of templates on the tilemap.
    2 # A multiplier that allows to enlarge the size of a template on display
    # You have to be careful with this one as it can modify the template
)
# You can also create it like this:
element2 = Element(
    10, 10,
    9, 12,
    2,
    tilemap # To work it needs to know where to get the templates from.
)
```

After creating it you can animate it with its `Element.add_animation` method
You can create several types and each has its specialties:
* The `idle` animation allows you to create a rotation of several templates at a precise rhythm in a loop. For each template you want to add, the coordinates from where you want to retrieve it (x-y coordinates on the tilemap) and the time to wait between each stage of the animation.
* Then will come soon the `action` type animation which as its name suggests will be triggered by pressing a particular key or a predefined action (like executing a function). This type of animation is still in development.
```python
from tilemap_tools import Tilemap

element = Tilemap("file.map").create_element(10, 10, 8, 6, 1)

animation_idle = element.add_animation(
    'idle', # The first argument is the animation type
    # Each animation type has its own parameters and some are mandatory
    images=[(3, 5), (9, 5)] # This is a list of tuples with each coordinate where the templates start
    # In this example we have 2 images, one starting at x = 3 and y = 5 and another at x = 9 and y = 5
    temps_anim=500, # Like this one which defines the time to wait between each image in milliseconds.
    # PS: can also be in the form of a list of times for each image
)
```
An element can have several idle animations stored and can switch between them at any time with its `Element.set_idle` method. For this, either you know the index of the animation you want to activate in the `idle` animations or you have its object at hand.

```python
# This program continues from the previous one

# Creating a 2nd different animation
animation_idle2 = element.add_animation(
    'idle',
    images = [(3, 15), (9, 15)]
    temps_anim = [300, 500] # The animation will stay 300 milliseconds with the first image then 500 with the 2nd
)

# You can activate this new animation in 2 ways
element.set_idle(1) # Activates the 2nd idle animation added to the element
# or
element.set_idle(animation_idle2)
```
When any animation is active, each image has its own hitbox. The `element.position_in_hitbox` method allows you to check if a single position (like the mouse position for example) would be in it, and the `element.compare_hitbox` method allows you to check if 2 elements are touching.

### **For a little extra**
With all these elements, the creator has developed several tools that he makes available, such as a way to know if `pyxel` is initialized with the `is_px_init` function. But also a way to retrieve a particular color with the `get_color` function, or even more interesting for some, a way to know exactly how long the game has been running with the `get_time` function.

## License

MIT License - see LICENSE for more details.

## Author

Julosse - julosse27110@gmail.com

## Acknowledgments
<font size=3>I hope this simple module will help you in creating your first games with Python.

Thank you for your attention and if you like this module, please spread the word so it can help even more people.</font>
