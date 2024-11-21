fetch('data/pokemon.json')
    .then(response => response.json())
    .then(data => {
        const list = document.getElementById('cobblemon-list');
        data.forEach(cobblemon => {
            const item = document.createElement('div');
            item.className = 'cobblemon-card';
            item.innerHTML = `
                <h3>${cobblemon.name}</h3>
                <p>Dex #: ${cobblemon.dex_number}</p>
                <p>Type: ${cobblemon.type.join(', ')}</p>
                <div class="palette">
                    ${cobblemon.color_palette.map(color => `<span style="background:${color};"></span>`).join('')}
                </div>
            `;
            list.appendChild(item);
        });
    })
    .catch(error => console.error('Error loading Pokémon data:', error));
