<h1 align="center">Welcome to NS-Shift-Planner 👋</h1>
<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0--beta-blue.svg?cacheSeconds=2592000" />
  <a href="LICENSE.txt">
    <img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg" />
  </a>
</p>



> Ns Planning app (Revamped from https://github.com/Eddrick-23/NS_SHIFT_PLANNER)

Access it here: https://ns-planner.onrender.com/

## 🚀 Features

- 🧩 **Interactive Grid UI**  
  Easily view and manipulate shift data in a responsive, user-friendly grid.

- ⚡ **Faster Grid Rendering with Ag-Grid**  
  Uses the high-performance [Ag-Grid](https://www.ag-grid.com/) for efficient rendering

- 🗂️ **Simple Session Management with Session IDs**  
  Resume or share planning sessions using lightweight session identifiers.

## Install and Run
### Install uv if not already installed
```
curl -Ls https://astral.sh/uv/install.sh | sh
```

### Install dependencies
```
uv venv
source .venv/bin/activate
uv pip install -r uv.lock
```

### Set up Firestore
- Session data is stored using [google firebase](https://console.firebase.google.com/u/0/)
- Set up a project and create a database
- Obtain your serviceAccountKey.json inject it using environment variables

### .env/Environment variables
```
GOOGLE_APPLICATION_CREDENTIALS=serviceAccountKey.json
FRONTEND_DOMAIN=https://frontend_domain (for deployment)
BACKEND_DOMAIN=https://backend_domain (for deployment)
BACKEND_PORT=8000
LRU_CACHE_SIZE=50
PRUNE_DB_INTERVAL=1
DB_COLLECTION_NAME=firestore-collection-name
DATA_EXPIRY_LENGTH=1
SCAN_CACHE_INTERVAL=30
HOST_NAME=localhost
ENVIRONMENT=DEV (set to PROD for deployment)
VERSION=current-app-version
API_KEY=secret-api-key
```

### Run in a container
```sh
docker compose up -d
```

## Built With
- [Firebase](https://firebase.google.com/) — Backend-as-a-Service for database
- [FastAPI](https://fastapi.tiangolo.com/) – Modern, fast web framework for building APIs
- [NiceGUI](https://nicegui.io/) – Python-based UI framework with real-time updates

## Data and Privacy

This app uses Firebase services to securely store and manage user data. Please refer to [Firebase's Privacy Policy](https://firebase.google.com/support/privacy) for details on how your data is handled.


## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

You are free to use, modify, and distribute this software, provided that any derivative works are also licensed under the GPL v3 and include proper attribution to the original author.

See the [LICENSE](LICENSE.txt) file for the full license text.


## Author

👤 **Eddrick**

* Github: [@Eddrick-23](https://github.com/Eddrick-23)
* LinkedIn: [@eddrick-livando](https://linkedin.com/in/eddrick-livando-8581ab228)


## Show your support

Give a ⭐️ if this project helped you!

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
