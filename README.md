<h1 align="center">Welcome to NS-Shift-Planner</h1>
<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-2.0.0--beta-blue.svg?cacheSeconds=2592000" />
  <a href="LICENSE.txt">
    <img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg" />
  </a>
</p>



> Ns Planning app (Revamped from https://github.com/Eddrick-23/NS_SHIFT_PLANNER)

Access it here: https://ns-planner.onrender.com/

## What's New (v2.0.0-beta)
- Ported frontend over to Vue JS
- Session management by http cookies <br>

See full [CHANGELOG.md](./CHANGELOG.md) for older versions.

## Features (what's new from old app)

-  **Interactive Grid UI**  
  Easily view and manipulate shift data in a responsive, user-friendly grid.

- **Faster Grid Rendering with Ag-Grid**  
  Uses the high-performance [Ag-Grid](https://www.ag-grid.com/) for efficient rendering

- **Automatic Session Management**  
  Sessions are managed using http cookies and saved to a database. No need to save as a zip file every time.

## Install and Run

### BACKEND
#### Install uv if not already installed
```
curl -Ls https://astral.sh/uv/install.sh | sh
```

#### Install dependencies
```
uv venv
source .venv/bin/activate
uv pip install -r uv.lock
```

#### Set up Firestore
- Session data is stored using [google firebase](https://console.firebase.google.com/u/0/)
- Set up a project and create a database
- Obtain your serviceAccountKey.json inject it using environment variables(paste it as a string)

#### Backend .env at project root
```
GOOGLE_APPLICATION_CREDENTIALS={serviceAccountKey.json}
FRONTEND_DOMAIN=https://frontend_domain (for deployment)
BACKEND_PORT=8000
FRONTEND_PORT=8080
LRU_CACHE_SIZE=50
PRUNE_DB_INTERVAL=1       //hours
DATA_EXPIRY_LENGTH=1      //days
SCAN_CACHE_INTERVAL=30    //min
DB_COLLECTION_NAME=firestore-collection-name
HOST_NAME=localhost
ENVIRONMENT=DEV (set to PROD for deployment)
VERSION=current-app-version
API_KEY=secret-api-key
```

### FRONTEND
```
cd src/frontend

npm install

npm run build

npm run dev
```

#### Frontend .env.local at src/frontend
```
VITE_FRONTEND_PORT=8080
VITE_VERSION=current-app-version
VITE_ENVIRONMENT="DEV"
VITE_DATA_SAVED_DURATION="1"

VITE_BACKEND_DOMAIN=http://localhost:8000 (change for prod)
VITE_SOURCE_CODE_URL=https://github.com/Eddrick-23/NS-Shift-Planner
```


### Run in a container
```sh
docker compose up -d
```

## Built With
- [Firebase](https://firebase.google.com/) - Backend-as-a-Service for database
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [Vue.js](https://vuejs.org/) - Progressive JavaScript framework for building user interfaces and single-page applications

## Data and Privacy

This app uses Firebase services to securely store and manage user data. Please refer to [Firebase's Privacy Policy](https://firebase.google.com/support/privacy) for details on how your data is handled.


## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

You are free to use, modify, and distribute this software, provided that any derivative works are also licensed under the GPL v3 and include proper attribution to the original author.

See the [LICENSE](LICENSE.txt) file for the full license text.


## Author

**Eddrick**

* Github: [@Eddrick-23](https://github.com/Eddrick-23)
* LinkedIn: [@eddrick-livando](https://linkedin.com/in/eddrick-livando-8581ab228)
