### Build and run in container
#### API
```
docker build -t planner-api -f src/backend/Dockerfile .
```
```
docker run --name plannerAPI -p 8000:8000 planner-api
```
#### Frontend
```
docker build -t nicegui -f src/frontend/Dockerfile
```
```
docker run --name nicegui -f src/frontend/Dockerfile
```



#### Docker compose
- Runs FastApi backend and NiceGUI frontend
__Run Service__
    ```
    docker compose up -d
    ```
Rebuild all services `docker compose up --build` <br>
Rebuild one service `docker compose build planner-api` <br>
Restart one service	`docker compose up -d planner-api` <br>
