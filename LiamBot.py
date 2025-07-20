# check bounds of map

from enum import Enum
# use when running locally

# from src.helper.helper.game import Game
# from src.lib.lib.models.tile_model import TileModel
# from src.lib.lib.interface.queries.typing import QueryType
# from src.lib.lib.interface.events.moves.typing import MoveType
# from src.lib.lib.interface.queries.query_place_meeple import QueryPlaceMeeple
# from src.lib.lib.interface.queries.query_place_tile import QueryPlaceTile

# -----------------------------------
from helper.game import Game
from lib.interact.tile import Tile
from lib.models.tile_model import TileModel
from lib.interface.queries.typing import QueryType
from lib.interface.events.moves.typing import MoveType
from lib.interact.structure import StructureType
from lib.interface.queries.query_place_meeple import QueryPlaceMeeple
from lib.interface.queries.query_place_tile import QueryPlaceTile


class BotState:
    def __init__(self) -> None:
        self.last_tile: TileModel | None = None

class Directions(Enum):
    TOP_EDGE = (0, -1)
    RIGHT_EDGE = (1, 0)
    BOTTOM_EDGE = (0, 1)
    LEFT_EDGE = (-1, 0)

def main() -> None:
    game = Game()
    bot_state = BotState()

    while True:
        # gets the query from the server
        query = game.get_next_query()
        print("query gotten", query)

        # given the query type wanted
        def choose_move(query: QueryType) -> MoveType:
            match query:
                case QueryPlaceTile() as q:
                    return handle_place_tile(game, bot_state, q)

                case QueryPlaceMeeple() as q:
                    return handle_place_meeple(game, bot_state, q)

        game.send_move(choose_move(query))

# logic of tile placement
def handle_place_tile(game : Game, bot_state: BotState, q):
    grid = game.state.map._grid
    # height = len(grid)
    # width = len(grid[0]) if height > 0 else 0

    # tiles currently in the player's hand
    my_tiles = game.state.my_tiles
    print(my_tiles)

    # Tiles placed on the map
    placed_tiles = game.state.map.placed_tiles


    for placed_tile in placed_tiles:
        for index, my_tile in enumerate(my_tiles):

            # Does the tile in hand have a river in it?
            river_tile = check_for_river(my_tile)
            print("River status: ", river_tile)



            for direction in Directions:
                for rotation in range(0, 4):
                    # if a valid placement is found
                    if check_placement_of_tile(game, placed_tile, my_tile, direction, rotation):

                        # Handle river tile
                        if river_tile:



                        bot_state.last_tile = my_tile
                        bot_state.last_tile.placed_pos = placed_tile.placed_pos[0] + direction.value[0], placed_tile.placed_pos[1] + direction.value[1]
                        return game.move_place_tile(q, my_tile._to_model(), index)



# Function that check if the current has a river in it
def check_for_river(tile: Tile)-> bool:

    for edge in Directions:
        if tile.internal_edges[edge] == StructureType.RIVER:
            return True
    return False;


def check_placement_of_tile(game: Game, placed_tile, my_tile, direction, rotation) -> bool:
    my_tile.rotate_clockwise(rotation)
    return game.can_place_tile_at(my_tile, placed_tile.placed_pos[0] + direction.value[0], placed_tile.placed_pos[1] + direction.value[1])


    # bot_state.last_tile =

    # for i in range(height):
    #     for j in range(width):
    #         if game.can_place_tile_at(my_tiles[0], i, j):
    #             print("hillo")
    #             return game.move_place_tile(q, my_tiles[0], 0)



# logic of whether to place meeple or not
def handle_place_meeple(game, bot_state, q):
    return game.move_place_meeple_pass(q)



if __name__ == "__main__":
    print("hey")
    main()
    # for direction in Directions:
    #     print(direction)
