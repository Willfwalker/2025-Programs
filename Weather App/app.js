// You'll need to sign up for a free API key at OpenWeatherMap
const API_KEY = process.env.OPENWEATHER_API_KEY;
const BASE_URL = 'https://api.openweathermap.org/data/2.5/weather';

// DOM elements
const cityInput = document.getElementById('city-input');
const searchBtn = document.getElementById('search-btn');
const weatherDisplay = document.getElementById('weather-display');
const errorMessage = document.getElementById('error-message');

// Add event listeners
searchBtn.addEventListener('click', getWeather);
cityInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        getWeather();
    }
});

async function getWeather() {
    const city = cityInput.value.trim();
    
    if (!city) {
        showError('Please enter a city name');
        return;
    }

    try {
        const response = await fetch(
            `${BASE_URL}?q=${city}&appid=${API_KEY}&units=metric`
        );
        
        if (!response.ok) {
            throw new Error('City not found');
        }

        const data = await response.json();
        displayWeather(data);
        errorMessage.textContent = '';
    } catch (error) {
        showError(error.message);
        weatherDisplay.innerHTML = '';
    }
}

function displayWeather(data) {
    const weather = {
        location: data.name + ', ' + data.sys.country,
        temperature: Math.round(data.main.temp),
        description: data.weather[0].description,
        humidity: data.main.humidity,
        windSpeed: data.wind.speed
    };

    weatherDisplay.innerHTML = `
        <h2>${weather.location}</h2>
        <p>${weather.temperature}°C</p>
        <p>${weather.description}</p>
        <p>Humidity: ${weather.humidity}%</p>
        <p>Wind Speed: ${weather.windSpeed} m/s</p>
    `;
}

function showError(message) {
    errorMessage.textContent = message;
} 