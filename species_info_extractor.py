import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_species_info(species_data):
    """
    Extract detailed Pokémon species information from the given data.
    This function aims to extract all relevant fields from the JSON data.
    """
    dex_number = species_data.get("nationalPokedexNumber", "Unknown")
    pokemon_name = species_data.get("name", "Unknown")
    primary_type = species_data.get("primaryType", "")
    secondary_type = species_data.get("secondaryType", "")
    egg_groups = ', '.join(species_data.get("eggGroups", []))
    catch_rate = species_data.get("catchRate", "Unknown")
    base_experience_yield = species_data.get("baseExperienceYield", "Unknown")
    base_friendship = species_data.get("baseFriendship", "Unknown")

    # Handle abilities as a list instead of a dictionary
    abilities = species_data.get("abilities", [])
    primary_ability = ""
    hidden_ability = ""
    secondary_abilities = []

    for ability in abilities:
        if ability.startswith("h:"):
            hidden_ability = ability[2:]
        elif primary_ability == "":
            primary_ability = ability
        else:
            secondary_abilities.append(ability)

    movement_type = species_data.get("movementType", "")
    rest_type = species_data.get("restType", "")

    height = species_data.get("height", 0.0)
    weight = species_data.get("weight", 0.0)
    base_scale = species_data.get("baseScale", 0.0)
    hitbox_width = species_data.get("hitbox", {}).get("width", 0.0)
    hitbox_height = species_data.get("hitbox", {}).get("height", 0.0)

    # Extract drops
    drops = species_data.get("drops", {}).get("entries", [])
    formatted_drops = [
        f"{drop.get('item', 'Unknown')} (Percentage: {drop.get('percentage', 0)})"
        for drop in drops
    ]
    drops_str = '; '.join(formatted_drops)

    # Extract base stats
    base_stats = species_data.get("baseStats", {})

    # Extract forms
    forms = []
    for form in species_data.get("forms", []):
        form_name = form.get("name", "Unknown Form")
        form_base_stats = form.get("baseStats", {})
        form_height = form.get("height", height)
        form_weight = form.get("weight", weight)
        form_abilities = form.get("abilities", [])
        form_moves = form.get("moves", [])
        form_evolutions = form.get("evolutions", [])

        forms.append({
            "form_name": form_name,
            "base_stats": form_base_stats,
            "height": form_height,
            "weight": form_weight,
            "abilities": form_abilities,
            "moves": form_moves,
            "evolutions": form_evolutions
        })

    # Extract evolutions
    evolutions = []
    for evolution in species_data.get("evolutions", []):
        evolves_to = evolution.get("result", "Unknown Evolution")
        evolution_level = None
        conditions = []

        for requirement in evolution.get("requirements", []):
            if requirement.get("variant") == "level":
                evolution_level = requirement.get("minLevel", None)
            else:
                conditions.append(requirement)

        evolutions.append({
            "evolves_to": evolves_to,
            "evolution_level": evolution_level,
            "conditions": conditions
        })

    # Extract moves
    moves = {
        "level_up": [move for move in species_data.get("moves", []) if move.startswith("1:")],
        "egg_moves": [move for move in species_data.get("moves", []) if move.startswith("egg:")],
        "tutor_moves": [move for move in species_data.get("moves", []) if move.startswith("tutor:")],
        "tm_moves": [move for move in species_data.get("moves", []) if move.startswith("tm:")]
    }

    # Extract labels
    labels = ', '.join(species_data.get("labels", []))

    return {
        "dex_number": dex_number,
        "pokemon_name": pokemon_name,
        "primary_type": primary_type,
        "secondary_type": secondary_type,
        "egg_groups": egg_groups,
        "catch_rate": catch_rate,
        "base_experience_yield": base_experience_yield,
        "base_friendship": base_friendship,
        "primary_ability": primary_ability,
        "hidden_ability": hidden_ability,
        "secondary_abilities": ', '.join(secondary_abilities),
        "movement_type": movement_type,
        "rest_type": rest_type,
        "height": height,
        "weight": weight,
        "base_scale": base_scale,
        "hitbox_width": hitbox_width,
        "hitbox_height": hitbox_height,
        "drops": drops_str,
        "base_stats": base_stats,
        "forms": forms,
        "evolutions": evolutions,
        "moves": moves,
        "generation": "Unknown",  # Adding a default value for generation
        "labels": labels
    }
