-- Create the hyrex database for the task queue
CREATE DATABASE hyrex;

-- Grant all privileges to the chatbot user on the hyrex database
GRANT ALL PRIVILEGES ON DATABASE hyrex TO chatbot;