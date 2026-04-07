# EV Predictor

A Machine Learning based Real-Time Remaining Useful Life Estimation and Fair Pricing Strategy for Electric Vehicle Battery Swapping Stations.

---

## About

This project is build as a part of the curriculum in the final year of 4-year B.Tech program @ SVCE, Tirupati.

---

## Team Details

<table>
  <tr>
    <th>Guided By</th>
    <td colspan="2">Dr. A.Ganesh., <sub><sup>M.Tech, Ph.D.(PDF)</sup></sub><br />
    Head of the Department,<br />Computer Science and Engineering,<br />SVCE, Tiruapti.
    </td>
  </tr>
  <tr>
    <th>Team Leader</th>
    <td>Bandi Anudeep Reddy</td>
    <td>22BFA05279</td>
  </tr>
  <tr>
    <th rowspan="3">Team Members</th>
    <td>Palem Monish</td>
    <td>22BFA05313</td>
  </tr>
  <tr>
    <td>Palagiri Mahesh Babu</td>
    <td>23BFA05L19</td>
  </tr>
  <tr>
    <td>Poluru Siri Sai</td>
    <td>22BFA05323</td>
  </tr>
</table>

---

## Prerequisites

- Visual Studio Code + Python Extensions (recommended)
- Git
- [**uv**](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) - A Python project and dependency manager
- MySQL (via Docker or direct install)

---

## Installation

#### Step 0: Install all the prerequisites

Install all the prerequisite software before deploying the server.

#### Step 1: Clone the git repo

```bash
git clone "https://github.com/Anudeep-CodeSpace/EV_Battery_Prediction.git"
cd EV_Battery_Prediction
```

#### Step 2: Install the Project Dependencies

```bash
uv sync
uv tool update-shell
```

#### Step 3: Setup the MySQL server & .env file

Setup MySQL endpoint before deploying the flask app.
```docker
docker run -d \
  --name mysql \
  -p 3306:3306 \
  -p 33060:33060 \
  -v mysql_data:/var/lib/mysql \
  -v $(pwd)/app/db.sql:/docker-entrypoint-initdb.d/init.sql \
  -e MYSQL_ROOT_PASSWORD=<your root password> \
  -e MYSQL_DATABASE=RUL \
  mysql:latest
```

update the .env file in the cloned project root folder.
```
#.env example
DB_HOST=localhost
DB_USER=root
DB_PASSWORD= # Your MYSQL root password
DB_PORT=3306
DB_NAME=RUL
```

#### Step 4: Run the Flask Server

```bash
uv run main.py
```

#### Step 5: Access the frontend

When running for the first time, it takes a couple of minutes to startup.
Frontend of the server is accessible at the endpoint specified in the output: Eg: http://127.0.0.1:5000

---

Please feel free to reachout in case of suggestions or bugs.
