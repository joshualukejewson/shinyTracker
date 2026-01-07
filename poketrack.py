import requests


class Pokemon:
    def __init__(self, name: str, sprite: str, shiny: str, count: int):
        self.name = name
        self.sprite = sprite
        self.shimy = shiny
        self.count = count

    def increment(self):
        self.count += 1

    def get_count(self):
        return self.count

    def reset_count(self):
        self.count = 0

    def __str__(self):
        return f"{self.name} - {self.sprite}"


def fetch_pokemon_data(pokemon_name: str, count: int) -> Pokemon:
    url = "https://pokeapi.co/api/v2/pokemon/{name}".format(name=pokemon_name)
    print(url)
    response = requests.get(url)
    raw_data = response.json()

    return Pokemon(
        raw_data["name"].lower(),
        raw_data["sprites"]["front_default"],
        raw_data["sprites"]["front_shiny"],
        count,
    )

def save_data(stored_pokemon):
    file_path = "static/storedPokemon.txt"

    with open(file_path, "w") as file:
        for pokemon in stored_pokemon.values():
            file.write("{name},{count}\n".format(name = pokemon.name, count=pokemon.count))


def retrieve_pokemon_data():

    stored_pokemon = {}
    file_path = "static/storedPokemon.txt"

    try:
        with open(file_path, "x") as file:
            pass
    except FileExistsError:
        print("{filename} already exists.".format(filename = file_path))

    with open(file_path, "r") as file:
        for line in file:
            data = line.split(",")
            pokemon_name = data[0].lower()
            encounters = int(data[1])
            stored_pokemon[data[0]] = fetch_pokemon_data(pokemon_name, encounters)

    return stored_pokemon

