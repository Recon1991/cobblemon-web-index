import React, { useEffect, useState } from 'react';
import { fetchPokemon } from './api';

function App() {
    const [pokemonList, setPokemonList] = useState([]);

    useEffect(() => {
        const getPokemon = async () => {
            const data = await fetchPokemon();
            setPokemonList(data);
        };
        getPokemon();
    }, []);

    return (
        <div className="App">
            <h1>Cobblemon Dex</h1>
            <div className="pokemon-grid">
                {pokemonList.map((pokemon) => (
                    <div key={pokemon.dex_number} className="pokemon-card">
                        <h2>{pokemon.pokemon_name}</h2>
                        <p>Type: {pokemon.primary_type}{pokemon.secondary_type && ` | ${pokemon.secondary_type}`}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
