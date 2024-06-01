import math

def calculate_grid_coordinates(start_xy, end_xy, row_col):
    start_x, start_y = start_xy
    end_x, end_y = end_xy
    row, col = row_col
    x_space = end_x - start_x
    y_space = end_y - start_y

    x_spacing = max(math.floor(x_space / col), 1)
    y_spacing = max(math.floor(y_space / row), 1)

    coordinates = []

    for y in range(start_y, end_y, y_spacing):
        for x in range(start_x, end_x, x_spacing):
            coordinates.append((x, y))

    return coordinates


# start_xy = (44, 105)
# end_xy = (164, 120)
# row_col = (1,24)
# grid_coordinates = calculate_grid_coordinates(start_xy, end_xy, row_col)

# print(grid_coordinates)

restock_quantities = {
    "a skill mastery orb (used to increase a player's total skill cap by 1)":   { "stack_size": (5,20),     "stack_quantity": (9,4),    "pos_xy": ((95,145),(105,145))},          #skill mastery orb
    "plant chemicals":                                                          { "stack_size": (100,),     "stack_quantity": (9,4),    "pos_xy": ((97,131),)},                   #plant chemicals
    "dyeable gilded gold carpet tile":                                          { "stack_size": (1,),       "stack_quantity": (10,),    "pos_xy": ((164,139),)},                   #carpet tile
    "pristine lumber":                                                          { "stack_size": (5,),       "stack_quantity": (2,),     "pos_xy": ((154,199),)},                   #pristine lumber
    "immaculate stone":                                                         { "stack_size": (5,),       "stack_quantity": (2,),     "pos_xy": ((164,199),)},                   #immaculate stone
    "an arcane scroll":                                                         { "stack_size": (100,),     "stack_quantity": (10,),    "pos_xy": ((44,143),),},                    #an arcane scroll
    "mastercrafting diagram":                                                   { "stack_size": (10,),      "stack_quantity": (3,),     "pos_xy": ((65,140),)},                    #mastercrafting diagram
    "prevalia coins [blessed]":                                                 { "stack_size": (1,),       "stack_quantity": (20,),    "pos_xy": ((44,90),)},                    #prevalia coins [blessed]
    "arcane essence":                                                           { "stack_size": (1000,),    "stack_quantity": (1,),     "pos_xy": ((108,130),)},                   #arcane essence
    "Cores":                                                                    { "stack_size": (1,5,20),   "stack_quantity": (2,2,1),  "pos_xy": ((44,83),(44,65),(45,74)),  "end_xy": ((164,83),(164,65),(163,74)), "row_col": (1,24) },   #Cores
    "Distils":                                                                  { "stack_size": (5,20),     "stack_quantity": (2,1),    "pos_xy": ((44,105),(44,120)),        "end_xy": ((164,105),(164,120)), "row_col": (1,24)  },          #Distils
    "Skill Mastery Scrolls":                                                    { "stack_size": (1,10),     "stack_quantity": (2,2),    "pos_xy": ((44,80),(44,104)),         "end_xy": ((164,80),(164,104)), "row_col": (1,33)  },           #Skill Scrolls
}

def render_stock_script_simple(item):
    data = restock_quantities[item]
    stack_sizes = data['stack_size']
    stack_quantities = data['stack_quantity']
    pos_coords = data['pos_xy']
    price_per = all_prices[item]





