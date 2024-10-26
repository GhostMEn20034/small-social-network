# Small Social Network API

# Features Implemented
 - [x] User registration <br>
 - [x] User login <br>
 - [x] API for managing posts <br>
 - [x] API for managing comments <br>
 - [x] Text content moderation for posts and comments. <br>
 - [x] Auto-reply feature. If the user enabled this feature for the post, other user's comments will be automatically replied to by Gemini AI after a specified amount of time (In minutes)

# Setup
**Note that the setup assumes you are using any Linux distribution**

### 1. Clone the project:
```bash
git clone https://github.com/GhostMEn20034/small-social-network.git
```
### 2. Change permissions for `init-database.sh`:
```bash
chmod +x init-database.sh
```
### 3. Create a `.env` file, using the following command:
```bash
touch .env
```

### 4. Open the file created above in whatever editor you want
### 5. Insert the next variables:
```bash
psql_connection_string=postgresql+asyncpg://<SQL_USER>:<SQL_PASSWORD>@db:5432/<SQL_DATABASE>
SQL_USER=your_db_user
SQL_PASSWORD=your_db_password
SQL_DATABASE=your_database_name
SUPER_USER_PWD=your_postgres_user_password
secret_key=2332333fdfdgsgd # Secret key required for signing JWT Tokens
sightengine_api_user=some_usr # Id of the user on sightengine API, See the next step to find out how to get the API user
sightengine_api_secret=123456  # The secret on sightengine API, See the next step to find out how to get the API secret
gemini_api_key=123456b # Your Gemini API key, See the next step to find out how to get this key
CELERY_BROKER_URL=redis://redis:6379/0 # Celery's broker URL. If you launch the app via docker-compose, you can keep it as it is
```
### 6. Get API Keys.
   6.1 To get `sightengine_api_user` and `sightengine_api_secret`, sign up at [sightengine's website](https://dashboard.sightengine.com/api-credentials), and go to [API keys](https://dashboard.sightengine.com/api-credentials) section. <br>
   6.2 To get the Gemini API key, go to [Google AI Studio](https://ai.google.dev/aistudio), click on "Sign in to Google AI studio", click on the button "Create API Key", then scroll down, click on "Create API key", choose the GoogleCloud project, copy the key 

# Running the App
### 1. Make sure you are in the root project directory.
### 2. Use the following command to run the app:
```bash
docker compose up -d --build
```
### 3. Go to [localhost:8000](http://localhost:8000)

# Running tests
### 1. Make sure you are in the root project directory.
### 2. Create env file with the name `.env.test`:
```bash
touch .env.test
```
### 3. Open the file in any editor and paste the same variables as in `.env` file:
```bash
psql_connection_string=postgresql+asyncpg://<SQL_USER>:<SQL_PASSWORD>@db:5432/<SQL_DATABASE>
SQL_USER=your_db_user
SQL_PASSWORD=your_db_password
SQL_DATABASE=your_database_name
SUPER_USER_PWD=your_postgres_user_password
secret_key=2332333fdfdgsgd # Secret key required for signing JWT Tokens
sightengine_api_user=some_usr # Id of the user on sightengine API, You can paste the mock value here
sightengine_api_secret=123456  # The secret on sightengine API, You can paste the mock value here
gemini_api_key=123456b # Your Gemini API key, You can paste the mock value here
CELERY_BROKER_URL=redis://redis:6379/0 # Celery's broker URL. You can paste the mock value here
```
### 4. Use the following command to run tests:
```
docker-compose -f docker-compose-test.yml --env-file .env.test up --build
```
### 5. After the tests' execution, click `Ctrl + C` to stop containers
