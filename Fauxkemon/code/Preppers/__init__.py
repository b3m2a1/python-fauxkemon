'''A module of prepper files

Includes:
    -Attack Prepper: Takes attack info as scraped from Bulbapedia and attempts to format it into an appropriate file
    -Tile Prepper: Takes a bunch of image files and converts them into map-ready format
    -Pokemon Prepper: Takes Bulbapedia data on Pokemon and tries to make it ready for use
    -Item Prepper: Takes item data from Bulbapedia and tries to make it ready for use
    -Prepper Window: Just a shell with all the preppers loaded'''
from Fauxkemon.code.Preppers.TilePrepper import *
from Fauxkemon.code.Preppers.PokemonPrepper import *
from Fauxkemon.code.Preppers.AttackPrepper import *
from Fauxkemon.code.Preppers.ItemPrepper import *
from Fauxkemon.code.Preppers.PrepperWindow import *