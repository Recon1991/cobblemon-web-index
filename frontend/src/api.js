import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export const fetchHello = async () => {
    const response = await axios.get(`${API_URL}/hello`);
    return response.data;
};

export const fetchPokemon = async () => {
    const response = await axios.get(`${API_URL}/pokemon`);
    return response.data;
};

