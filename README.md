#### Build and Run API in container
```
docker build -t planner-api -f src/backend/Dockerfile .
```
```
docker run --name plannerAPI -p 8000:8000 planner-api
```
