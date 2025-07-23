from _typeshed import SizedBuffer
from dill import check

#### DISCLAIMER ####
# This was produced with the assistance of GPT 4o

from enum import Enum
from helper.game import Game
from lib.interface.events.moves.move_place_meeple import (
    MovePlaceMeeple,
    MovePlaceMeeplePass,
)
from lib.interface.events.moves.move_place_tile import MovePlaceTile
from lib.interface.queries.typing import QueryType
from lib.interface.queries.query_place_tile import QueryPlaceTile
from lib.interface.queries.query_place_meeple import QueryPlaceMeeple
from lib.interface.events.moves.typing import MoveType
from lib.models.tile_model import TileModel
from lib.interact.tile import Tile, TileModifier
from lib.interact.structure import StructureType


class Directions(Enum):
    TOP_EDGE = (0, -1)
    RIGHT_EDGE = (1, 0)
    BOTTOM_EDGE = (0, 1)
    LEFT_EDGE = (-1, 0)

class BotState:
    def __init__(self) -> None:
        self.last_tile: TileModel | None = None


def main() -> None:
    game = Game()
    bot_state = BotState()

    while True:
        query = game.get_next_query()

        def choose_move(query: QueryType) -> MoveType:
            match query:
                case QueryPlaceTile() as q:
                    return handle_place_tile(game, bot_state, q)

                case QueryPlaceMeeple() as q:
                    return handle_place_meeple(game, bot_state, q)

        game.send_move(choose_move(query))


def handle_place_tile(
    game: Game, bot_state: BotState, query: QueryPlaceTile
) -> MovePlaceTile:
    """Logic for placing the tiles"""

    # Getting the game grid
    grid = game.state.map._grid
    grid_height = len(grid)
    grid_width = len(grid[0]) if height > 0 else 0

    # Getting the Current tiles in hand
    my_tiles = game.state.my_tiles

    # Getting all the tiles currently placed on the board
    placed_tiles = game.state.map.placed_tiles

    # Checking if we have a river tile in hand
    # Store all river tiles in a list
    river_tiles = []
    for tile in my_tiles:
        if check_for_river(tile):
            river_tiles.append(tile)

    # Handling all the river tiles first
    if len(river_tiles):

        # Choosing certain river tile if there are multiple
        current_r_tile = get_best_river_tile(river_tiles)

        # Find avaliable position to place river tile
        adjacent_tile, pos_x, pos_y, direction = find_place_for_river_tile(game, placed_tiles, current_r_tile)

    return

# Function that check if the given tile has a river in it
def check_for_river(tile: Tile)-> bool:

    # Checking tile type based on tile_id
    # river tiles follow "R*"
    if "R" in tile.tile_id:
        return True;
    return False;

# Function that return the best river tile
# Priority (Monastery, city, bridge / road, just river)
def get_best_river_tile(river_tiles: list[Tile])-> Tile:

    # Storing all river tiles that have either a city or road in them
    city_tiles = ["R1", "R4", "R7" ]
    road_tiles = ["R3", "R6" ]

    best_tile = river_tiles[0]
    for r_tile in river_tiles:

        # Does this tile have modifiers ( lookin for Monastery)
        if len(r_tile.modifiers):
            if r_tile.modifiers[0] == TileModifier.MONASTARY:
                return r_tile

        elif r_tile.tile_id in city_tiles:
            best_tile = r_tile

        elif r_tile.tile_id in road_tiles and best_tile.tile_id not in city_tiles:
            best_tile = r_tile

    return best_tile


'''Function for finding a applicable position for a river tile'''
def find_place_for_river_tile(game: Game, placed_tiles: list[Tile], river_tile: Tile):

    # Search all placed tiles and find a spot where the river tile can be placed
    # return the first applicable position
    for p_tile in placed_tiles:
        applicable_placement_positions= check_adjacet_space_for_new_tile_placement(game, river_tile, p_tile)

        # check for uturn


    return

'''Function which checks if a new tile can be placed next to another tile given:
    a new tile,
    and an already placed tile
    return position coordinates of all applicable spaces for tile placement adjacent to
    repective placed tile'''
def check_adjacet_space_for_new_tile_placement(game: Game, new_tile: Tile, placed_tile: Tile):

    # Goes through all the directions
    applicable_positions = []
    for direction in Directions:
        x_pos = placed_tile.placed_pos[0] + direction.value[0]
        y_pos= placed_tile.placed_pos[1] + direction.value[1]
        if game.can_place_tile_at(new_tile, x_pos, y_pos):
                applicable_positions.append((x_pos, y_pos))

    print("Applicable direction are:", applicable_positions)
    return applicable_positions

##############################
# Logic for meeple below this

def handle_place_meeple(
    game: Game, bot_state: BotState, query: QueryPlaceMeeple
) -> MovePlaceMeeple | MovePlaceMeeplePass:
    """Try to place a meeple on the tile just placed, or pass."""
    assert bot_state.last_tile is not None
    structures = game.state.get_placeable_structures(bot_state.last_tile)

    x, y = bot_state.last_tile.pos
    tile = game.state.map._grid[y][x]

    assert tile is not None

    tile_model = bot_state.last_tile
    bot_state.last_tile = None

    if structures:
        for edge, _ in structures.items():
            if game.state._get_claims(tile, edge):
                continue

            else:
                return game.move_place_meeple(query, tile_model, placed_on=edge)

    return game.move_place_meeple_pass(query)


if __name__ == "__main__":
    main()
