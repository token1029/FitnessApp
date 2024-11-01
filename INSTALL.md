# Steps for execution

## Step 1:
Install MongoDB using the following link:

For windows:
https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows

For macOS:
https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/

## Step 2:

Run MongoDB locally to be used by the application:

For Windows(If You Did Not Install MongoDB as a Windows Service):
https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-windows/#std-label-run-mongodb-from-cmd


For macOS:
`brew services start mongodb-community@8.0`

## Step 2:
Git Clone the Repository

    git clone https://github.com/SEFall24-Team61/FitnessAppNew.git

## Step 3:
Install the required packages by running the following command in the terminal

    pip install -r requirements.txt

## Step 4:
Run the following command in the terminal

    python application.py

## Step 5:
Open the URL in your browser:  
 http://127.0.0.1:5000/

> NOTE:
If you get error regarding any of the following packages - pymongo and bson, then try running the following commands to resolve the error :

    pip uninstall bson
    pip uninstall pymongo
    pip install pymongo
