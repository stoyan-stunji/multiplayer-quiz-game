## 🎮 Multiplayer Quiz Game

A simple multiplayer quiz game hosted online using **ngrok**. Follow the steps below to set up and run the game server.

## 🚀 Setup Instructions

### 1. Install ngrok
- Download **ngrok** from the official site or from the Microsoft store;
- Open a terminal (PowerShell or CMD) and authenticate with your ngrok token:
```
   ngrok config add-authtoken <YOUR_AUTHTOKEN>
```
- **<YOUR_AUTHTOKEN>** is the token generated in your profile when registered to the offical site of **ngrok**

### 2. Install Python Dependencies
```
pip install flask flask-socketio eventlet
pip install requests
```

### 3. Start the Game Server
- Navigate to the folder with the downloaded game:
```
cd path\to\your\project
```
- Run the game using:
```
python server.py
```

### 4. Playing the game
- When the server starts, you’ll see output like this:
```
Loaded X questions from questions.json
Starting server on port YYYY...

🎉 Game is live! Open this on your phone:
https://[generated-symbols].ngrok-free.app/join?name=YourName
Leaderboard: https://[same-generated-symbols].ngrok-free.app/leaderboard
```

- Open the join link on your phone or browser;
- Replace **YourName** with any desired name. Example:
```
https://[same-generated-symbols].ngrok-free.app/join?name=Stoyan
```
- You can visit the leaderboard link to see scores update in real time.

### 5. Stopping the game:
- In the terminal where the server is running, type:
```
stop
```

### 6. Changing the questions:
- You can change the questions by replacing the questions.json file;
- But it has to follow the original structure:
```
[
    {
        "question": "0. How much is 2+2?",
        "options": ["A) 4", "B) 44", "C) 444", "D) 4444"],
        "correct": "A",
        "points": {"A": 1, "B": 0, "C": 0, "D": 0}
    },
    {
        ...
    }
]
``` 

## 📸 Screenshots
-
-

