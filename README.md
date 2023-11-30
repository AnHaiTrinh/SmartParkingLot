# Smart Parking Lot
## Description

## Installation
Make sure you have Git installed in your machine. Check by running:
```bash
git --version
```
If not installed, follow the instructions in the [Git website](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
Clone this repository:
```bash
git clone https://github.com/AnHaiTrinh/SmartParkingLotBackend.git
```

## Run the project
Create an *app.env* file in the root directory with the following content:
```
DB_DATABASE
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
REDIS_HOST
REDIS_PORT
JWT_ACCESS_SECRET_KEY
JWT_REFRESH_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS
ALGORITHM
```
### Run with Docker (Preferred)
Make sure Docker and docker-compose are installed in your machine. 
Check by running:

```bash
docker -v
docker compose version
```
If not installed, follow the instructions in the [Docker website](https://docs.docker.com/get-docker/).

Create a *db.env* file in the root directory with the following content:
```
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Make sure it matches the environment variables declared in *app.env*. Then, run the following command in the root directory:
```bash
docker compose up -d
```
Once the containers are up and running, you can access the API at http://localhost:8000.

To remove the containers, run:
```bash
docker compose down
```

### Run locally
Make sure you have Python 3.9 installed in your machine. 
ALso replace the environment variables in *app.env* with the values corresponding to your Postgres instance.

Create a virtual environment and activate it:
```bash
python3 -m venv venv

source venv/bin/activate # Linux
venv\Scripts\activate # Windows
```
Install the dependencies:
```
pip install -r requirements.txt
```

Run the main app:
```bash
uvicorn app.main:app
```
Once the server is up and running, you can access the API at http://localhost:8000.

## Development
To automatically update the app container when changes are made, run:
```
docker compose watch
```