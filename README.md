 Game Matchmaking System in Python

This project was created to learn and implement the principles of a matchmaking system for 5v5 team-based games, inspired by titles like Heroes of the Storm.

## 🌟 Key Features

- **Role-based Matchmaking**: Implements team composition rules requiring a minimum of '1 Tank, 1 Healer'.
- **10-Player Match Creation**: Forms a complete game (Match) by finding two teams of five (Team A and Team B).
- **MMR-based Team Balancing**: After forming two teams, it compares their average MMR to ensure a balanced match.
- **Data Management**:
    - `characters.json`: Manages the list of available heroes and their basic information.
    - `PlayerRepository`: Implements a repository layer to manage player data, designed for future database integration.
- **Unit Testing**: Uses `pytest` to verify the correctness of core business logic (team composition, MMR calculation, etc.).

## 🛠️ Tech Stack

- **Language**: Python
- **Web Framework**: FastAPI
- **Web Server**: Uvicorn
- **Data Validation**: Pydantic
- **Testing**: Pytest

## 📂 Project Structure

```
matchmaking-fastapi/
│
├── .gitignore                 # Specifies intentionally untracked files to ignore
├── characters.json            # JSON file defining the character roster
├── requirements.txt           # List of project dependencies
│
├── matchmaking/               # Main package for core logic
│   ├── core/                  # Core project configuration package
│   │   └── config.py          # Manages constants like matching rules
│   ├── data/                  # Data source management package
│   │   ├── roster.py          # Reads and manages characters.json
│   │   └── player_repository.py # Creates and stores player data
│   ├── domain/                # Data models (Pydantic) package
│   │   └── models.py          # Player, Role, Match, etc.
│   └── service/                 # Business logic package
│       └── matchmaking_service.py # The actual matchmaking logic
│
├── tests/                     # Folder for test code
│   └── test_service.py        # Tests for the matchmaking.service module
│
├── main.py                    # Entry point for the FastAPI server (incomplete)
└── run_simulation.py          # Script to run the logic manually without a server
```

## 🚀 Setup and Execution

1.  **Clone the repository**
    ```bash
    git clone [repository URL]
    cd matchmaking-fastapi
    ```

2.  **Create and activate a virtual environment**
    ```bash
    # Create a virtual environment (one-time setup)
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate

    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the project**
    There are two ways to run the project:

    -   **A) Run the simulation script (to check logic without a server)**
        ```bash
        python run_simulation.py
        ```

    -   **B) Run unit tests (to automatically verify logic)**
        ```bash
        pytest
        ```

## 🔮 Future Improvements

- **Implement API Endpoints**: Implement practical RESTful API endpoints for external clients to request matches and get results, beyond the current simulation/testing approach.
- **Database Integration**: Refactor `PlayerRepository` to integrate with a real RDBMS (e.g., PostgreSQL).
- **Advanced Balancing Logic**: Implement a more sophisticated balancing algorithm that considers factors beyond MMR, such as recent win rates or role-specific proficiency.
- **Further Enhancements**: Utilize Redis to publish a "match found" event, creating a more scalable, event-driven architecture.

## 📝 Key Design Decisions (Q&A)

- **Q: Shouldn't we find players with similar MMR during the team formation process (i.e., find an optimal group of 10)?**

  **A:** While this theoretically creates the most balanced teams, it is computationally complex and slow (related to the subset sum problem). It can lead to extremely long queue times while the system searches for a "perfect" combination. Therefore, a more practical approach was taken: first, form two teams that satisfy the role requirements. Then, check the balance between them. If the average MMR difference is small, the match proceeds. If it's large, the system can attempt to swap players. If balancing still fails, the match is disbanded, and players are returned to the queue. This prioritizes reasonable queue times over perfect balance.

- **Q: In a real game, how are 10 players sent to a game session after a match is made?**

  **A:** Instead of passing the `Match` object directly between services, the system broadcasts a "match found" event, typically using a message broker like Redis Pub/Sub. A separate `SessionService` listens for this event and creates a unique game session in the database. A `GameServerManager` then allocates a dedicated game server from a fleet of available servers. Finally, the connection information (IP, port) for this dedicated server is sent to all 10 players (usually via WebSockets), who then connect to it to start the game.