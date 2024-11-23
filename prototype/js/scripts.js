// Fetch Cobblemon data from the JSON file
fetch('data/pokemon.json')
    .then(response => {
        // Check if the response is okay
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const list = document.getElementById('cobblemon-list');

        // Check if the list element exists
        if (!list) {
            console.error("Element with ID 'cobblemon-list' not found.");
            return;
        }

        // Populate the list with Cobblemon data
        data.forEach(cobblemon => {
            const item = document.createElement('div');
            item.className = 'cobblemon-card';
            item.innerHTML = `
                <h3>${cobblemon.name}</h3>
                <p>Dex #: ${cobblemon.dex_number}</p>
                <p>Type: ${cobblemon.type.join(', ')}</p>
                <div class="palette">
                    ${cobblemon.color_palette
                        .map(color => `<span style="background:${color}; display: inline-block; width: 20px; height: 20px; margin: 0 5px;"></span>`)
                        .join('')}
                </div>
            `;
            list.appendChild(item);
        });

        console.info('Cobblemon data loaded successfully.');
    })
    .catch(error => {
        // Log any errors during the fetch or processing
        console.error('Error loading Cobblemon data:', error);
    });
