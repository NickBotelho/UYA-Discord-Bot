docker build -t uya-players-online .
docker run --env-file env.list -it uya-players-online
