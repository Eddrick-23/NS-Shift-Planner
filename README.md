#### Build and Run API in container
```
docker build -t planner-api -f src/backend/Dockerfile .
```
```
docker run --name plannerAPI -p 8000:8000 planner-api
```


#### Docker compose
- Runs FastApi 
- Runs Redis Cache
- Runs Redis insight(gui tool) <br>
__Run Service__
    ```
    docker compose up -d
    ```
Rebuild all services `docker compose up --build` <br>
Rebuild one service `docker compose build planner-api` <br>
Restart one service	`docker compose up -d planner-api` <br>
