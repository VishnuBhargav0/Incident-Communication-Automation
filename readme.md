# Incident Communication Automation
This application automatically generates tickets in Zendesk by reading user emails and details from a Google Sheet. The application is designed to be used in case of incidents where communication with multiple users is required.

## Features
- Can read and import the emails from a Google sheet and create tickets with assignees as those emails. 
- Can replace placeholders in the body text, so the tickets that are created are personalized for each user. 
- Supports exponential backoff retry strategy in case of connection errors to retry the failed ticket creation.
- Interactive UI that can be used to automate the email creation.


## Requirements
1. To host this application and to get the application running, please first add in a key.json file in the root directory of the repository. More information on how to download and add this file is present [below](#Installation).
2. The way this is designed is that it can only take customer emails as inputs from a Google Sheet. There should be a Google Sheet that contains all the emails for which a ticket needs to be created. This Google sheet should also be shared with the email that is present in the key.json file that was added above.
2. A new ticket will be created for every row in that Google sheet, if there is a requirement to loop in multiple emails in a single ticket [as cc], please add the emails in a single cell delimited by a comma.
3. Any Placeholders in the body text need to follow the [below](#Installation) conventions.
4. A zendesk email and password that will authenticate the requests and to which the generated tickets will be assigned to. (2FA IF TURNED ON NEEDS TO BE TURNED OFF FOR THIS TO WORK.)


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/VishnuBhargav0/Incident-Communication-Automation.git
2. Install the requirements. 
    ``` bash
   cd Incident-Communication-Automation
   pip install requirements.txt
    ```

### downloading the key.json file
1. Create a project in the [Google Developers Console](https://console.cloud.google.com/)
2. Enable the Google Sheets API and Google Drive API using the Enable API & Services button on the UI.
3. Create a service account and download the JSON key file.
4. Rename the JSON key file to key.json and place it in the root of the project directory.

### Placeholder naming conventions
All the placeholders in the body text must follow the below naming conventions. 
##### For a placeholder that is a key and value pair need to be named as below: 
####
```
__placeholder__1: __placeholder_value__1
```

##### Any individual placeholder can be named as below: 
####
```
__placeholder_value__2
```

### Usage
1. Start the FastAPI server:
    ```
    uvicorn main:app --reload
    ```
2. Open your web browser and go to http://127.0.0.1:8000. In the Home page, fill out the form with the below details:
    1. document_name: The name of the Google Sheet document.
    2. worksheet_number: The index of the worksheet containing the data (0-based index).
    3. email_col_index: The index of the column containing the email addresses (0-based index).
3. Click "Submit" button, this should display all the emails that were read from the google sheet, give the below information in the ticket creation form and Click "Create Ticket" to generate the tickets.
    1. req_email: The email of the requester, all the tickets that will be created will be assigned to this email.
    2. password: The password thats used to login to zendesk with the above email. 
    3. subject: The subject of the ticket.
    4. tags: Tags to be added to the ticket (comma-separated).
    5. body: The body of the ticket with placeholders.
    6. Placeholders: Number of placeholders and their respective column index and name. 
