# Collabel - Collaborative Labeling Game

A real-time collaborative labeling game built with Django and Vue.js that allows multiple workers to collaboratively label data while competing and cooperating in a gamified environment.

## Features

- **Real-time Collaboration**: WebSocket-based communication for live updates
- **Multiple Game Modes**: Normal, chat-only, no-chat, and individual modes
- **Gamification**: Scoring system, levels, leaderboards, and visual elements
- **Quality Control**: Honeypot questions and agreement scoring
- **Multi-modal Data**: Support for text and image-based labeling tasks
- **Research Ready**: Comprehensive logging and MTurk integration support

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone the Repository
```bash
git clone you@example.com:WWEQE/collabel.git
cd collabel
```

### 2. Run with Docker Compose
```bash
# Navigate to local deployment directory
cd deploy_local

# Start all services (defaults to normal mode)
sudo docker-compose down && sudo docker-compose up --build
```

## Testing the Application

### Room Assignment Testing
1. Open multiple browser tabs with different worker IDs:


   - [http://[::]:8000/game/?workerId=1](http://[::]:8000/game/?workerId=1)
   - [http://[::]:8000/game/?workerId=2](http://[::]:8000/game/?workerId=2)
   - [http://[::]:8000/game/?workerId=3](http://[::]:8000/game/?workerId=3)
   - [http://[::]:8000/game/?workerId=4](http://[::]:8000/game/?workerId=4)
   - [http://[::]:8000/game/?workerId=5](http://[::]:8000/game/?workerId=5)

   **Note**: You need to create exactly 5 pending workers for room assignment to work. You can use any worker IDs you prefer, but you must have 5 workers in the pending state.

2. Watch real-time updates in browser tabs

### Game Modes
The application supports different game modes that can be set using environment files located in the project root:

- **normal** (default): Full collaborative experience with chat, scoring, and levels
- **chat_only**: Only chat functionality enabled
- **no_chat**: No chat, just labeling tasks  
- **individual**: Single-player mode

#### Running Different Game Modes
```bash
# Normal mode (default - no env file needed)
sudo docker-compose down && sudo docker-compose up --build

# Chat only mode
sudo docker-compose down && sudo docker-compose --env-file ../chat_only.env up --build

# No chat mode
sudo docker-compose down && sudo docker-compose --env-file ../no_chat.env up --build

# Individual mode
sudo docker-compose down && sudo docker-compose --env-file ../individual.env up --build
```

## Development

### Project Structure
```
collabel/
├── collabel/                 # Django project settings
├── game/                     # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # HTTP views
│   ├── consumers.py         # WebSocket consumers
│   ├── routing.py           # WebSocket routing
│   └── management/          # Django management commands
├── collabel_front/          # Vue.js frontend
│   ├── src/                 # Source code
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── static/                  # Built frontend assets
├── resource/                # Datasets and resources
└── deploy_local/            # Docker deployment configuration
```

### Key Technologies
- **Backend**: Django with Django Channels for WebSocket support
- **Frontend**: Vue.js 3 with Vite build tool
- **Database**: SQLite (development)
- **Message Broker**: Redis for WebSocket communication
- **Web Server**: Nginx reverse proxy

### Key Files
- **Models**: `game/models.py` - Database schema and business logic
- **Views**: `game/views.py` - HTTP request handling
- **Consumers**: `game/consumers.py` - WebSocket message handling
- **Routing**: `game/routing.py` - WebSocket URL patterns
- **Frontend**: `collabel_front/src/` - Vue.js components and logic

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Stop existing services: `docker-compose down`
   - Check for other services using ports 80, 8000, or 8001

2. **Build Issues**
   - Clean and rebuild: `sudo docker-compose down && sudo docker-compose up --build`
   - Check Docker logs: `sudo docker-compose logs`


## Production Deployment

For production deployment, see the `deploy/` directory for Docker-based production configuration with nginx reverse proxy.

