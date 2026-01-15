# Django Blackjack Web Application Plan

## Overview
Build a Django web application for Blackjack with user authentication and PostgreSQL database.

## Requirements
- **Game**: Blackjack only (from existing `learning_blackjack.py`)
- **Auth**: Simple username/password login
- **Database**: PostgreSQL
- **Location**: Project root directory

---

## Project Structure

```
MyDjangoApp/
├── manage.py
├── mydjangoapp/                      # Project settings
│   ├── settings.py                   # PostgreSQL config
│   └── urls.py                       # Root URLs
│
├── accounts/                         # Auth app
│   ├── models.py                     # UserProfile (optional)
│   ├── views.py                      # Login, logout, register
│   ├── urls.py
│   └── templates/accounts/
│       ├── login.html
│       └── register.html
│
├── game/                             # Blackjack game app
│   ├── models.py                     # GameSession, GameHistory
│   ├── views.py                      # deal, hit, stand views
│   ├── urls.py
│   └── templates/game/
│       ├── table.html                # Main game UI
│       └── history.html              # Game history
│
├── core/                             # Shared utilities
│   └── blackjack_engine.py           # Adapted from learning_blackjack.py
│
├── static/css/game.css               # Styling
├── templates/base.html               # Base template
└── requirements.txt
```

---

## Database Models

### GameSession (Active games)
- `user` (FK to User)
- `player_cards` (JSONField)
- `dealer_cards` (JSONField)
- `player_score`, `dealer_score`
- `status` (in_progress, player_win, dealer_win, etc.)
- `is_player_turn` (boolean)

### GameHistory (Completed games)
- `user` (FK to User)
- `player_final_cards`, `dealer_final_cards`
- `result` (win, loss, push, blackjack)
- `played_at`

---

## Key Views

| URL | View | Description |
|-----|------|-------------|
| `/` | `game_table` | Main game interface |
| `/new/` | `new_game` | Start new game (deal cards) |
| `/hit/` | `hit` | Player draws card |
| `/stand/` | `stand` | Player stands, dealer plays |
| `/history/` | `game_history` | View past games |
| `/accounts/login/` | `login_view` | User login |
| `/accounts/register/` | `register_view` | User registration |

---

## Implementation Steps

### Step 1: Project Setup
- Create Django project: `django-admin startproject mydjangoapp` ✅
- Create apps: `accounts`, `game`
- Configure PostgreSQL in settings.py
- Create `requirements.txt` (Django, psycopg2-binary)

### Step 2: Core Engine
- Copy blackjack logic from `learning_blackjack.py` to `core/blackjack_engine.py`
- Functions: `deal_card()`, `calculate_score()`, `is_blackjack()`, `determine_winner()`

### Step 3: Models
- Create GameSession and GameHistory models
- Run migrations

### Step 4: Authentication
- Implement login/register views using Django's built-in forms
- Create login and register templates

### Step 5: Game Views
- Implement `new_game`, `hit`, `stand` views
- Create game table template with card display
- Add game history view

### Step 6: Styling
- Add CSS for cards and game table
- Style authentication forms

### Step 7: Testing
- Test game flow manually
- Write Django view tests

---

## Files to Modify/Create

| File | Action |
|------|--------|
| `learning_blackjack.py` | Source (read only) |
| `core/blackjack_engine.py` | Create (adapt from learning_blackjack.py) |
| `game/models.py` | Create models |
| `game/views.py` | Create game logic |
| `accounts/views.py` | Create auth views |
| `templates/` | Create all templates |

---

## Verification

1. **Setup**: Run `python manage.py runserver` - server starts without errors
2. **Auth**: Register new user, login, logout works
3. **Game**:
   - Click "Deal Cards" starts new game
   - "Hit" adds card to player hand
   - "Stand" triggers dealer play and shows result
   - Game history shows past games
4. **Database**: Check PostgreSQL has game records after playing
