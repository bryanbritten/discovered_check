function fetchChessDotComGames(username, year, month) {
    if (year < 2000) {
        throw new Error("API data fetching is only supported for the year 2000 or later.");
    }
    month = month < 10 ? `0${month}` : month;
    const url = `https://api.chess.com/pub/player/${username}/games/${year}/${month}`;
    fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(`Found ${data.games.length} games.`);
    })
    .catch(error => {
        console.error(`Error fetching data: ${error}`);
    });
}

function test() {
    alert("This is working!");
}