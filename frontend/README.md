# Agent X - React Frontend

Modern React-based user interface for the Agent X task automation system.

## Features

- 🎨 Modern dark theme UI with glassmorphism effects
- 🔐 JWT-based authentication (Login/Signup)
- 🌐 Google OAuth 2.0 integration
- 🤖 11+ AI Agent interfaces
- 📱 Fully responsive design
- ⚡ Framer Motion animations

## Quick Start

### Prerequisites

- Node.js 18+ (LTS recommended)
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Configuration

1. Copy the environment example file:
```bash
cp .env.example .env
```

2. Update the `.env` file with your Google Client ID:
```
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000
```

### Development

```bash
npm start
```

The app will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
```

## Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API (or Google Identity Services)

### Step 2: Configure OAuth Consent Screen

1. Navigate to **APIs & Services > OAuth consent screen**
2. Select **External** (for testing) or **Internal** (for organization)
3. Fill in the required fields:
   - App name: `Agent X`
   - User support email: Your email
   - Developer contact: Your email
4. Add scopes: `email`, `profile`, `openid`
5. Add test users if using External type

### Step 3: Create OAuth Credentials

1. Navigate to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Select **Web application**
4. Configure:
   - Name: `Agent X Web Client`
   - Authorized JavaScript origins:
     - `http://localhost:3000` (development)
     - `https://your-production-domain.com` (production)
   - Authorized redirect URIs:
     - `http://localhost:3000` (development)
     - `https://your-production-domain.com` (production)
5. Click **CREATE**
6. Copy the **Client ID** and add it to your `.env` file

### Step 4: Update Backend

Add the same Client ID to the backend `.env` file:
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── Layout.js        # Main layout with sidebar
│   ├── context/
│   │   └── AuthContext.js   # Authentication state management
│   ├── pages/
│   │   ├── Login.js         # Login page with Google OAuth
│   │   ├── Signup.js        # Registration page
│   │   └── Dashboard.js     # Main dashboard with agents
│   ├── services/
│   │   └── api.js           # Axios API configuration
│   ├── styles/
│   │   └── index.css        # Global styles
│   ├── App.js               # Main app component
│   └── index.js             # Entry point
├── .env.example
└── package.json
```

## Available Routes

| Route | Description |
|-------|-------------|
| `/login` | Login page |
| `/signup` | Registration page |
| `/dashboard` | Main dashboard |
| `/agents/:type` | Specific agent page |
| `/history` | Task history |
| `/settings` | User settings |

## Tech Stack

- **React 18** - UI framework
- **React Router** - Navigation
- **Framer Motion** - Animations
- **Axios** - HTTP client
- **@react-oauth/google** - Google OAuth
- **Lucide React** - Icons
- **React Hot Toast** - Notifications

## Styling

The UI uses a modern dark theme with:
- CSS custom properties for theming
- Glassmorphism effects
- Smooth animations
- Responsive grid layouts

## License

MIT License
