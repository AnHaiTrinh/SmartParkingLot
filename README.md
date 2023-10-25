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
Create a *.env* file in the root directory with the following content:
```
DB_DATABASE=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```
### Run with Docker (Preferred)
Make sure Docker and docker-compose are installed in your machine. 
Check by running:

```bash
docker -v
docker-compose -v
```
If not installed, follow the instructions in the [Docker website](https://docs.docker.com/get-docker/).

Then, run the following command in the root directory:
```bash
docker-compose up -d
```
Once the containers are up and running, you can access the API at http://localhost:8000.

To remove the containers, run:
```bash
docker-compose down
```

### Run locally
Make sure you have Python 3.9 installed in your machine. and access to an PostgreSQL database.

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