# Incident Communication Automation
This application automatically generates tickets in Zendesk by reading user emails and details from a Google Sheet. The application is designed to be used in case of incidents where communication with multiple users is required.

## Features
- Can read and import the emails from a Google sheet and create tickets with assignees as those emails. 
- Can replace placeholders in the body text, so the ticket that are created are personalized for each user. 
- Supports exponential backoff retry strategy in case of connection errors to retry the failed ticket creation.
- Interactive UI that can be used to automate the email creation.


## Requirements
1. To host this application and to get the application running, please first add in a key.json file in the root directory of the repository. More information on how to download and add this file is present [below](#downloading the key.json file).
2. The way this is designed, it can only take customer emails as inputs from a Google Sheet. There should be a Google Sheet that contains all the emails for which a ticket needs to be created. This Google sheet should also be shared with the email that is present in the key.json file that was added above.
2. A new ticket will be created for every row in that Google sheet, if there is a requirement to loop in multiple emails in a single ticket [as cc], please add the emails in a single cell delimited by a comma.
3. Any Placeholders in the body text need to follow the [below](#Placeholder naming conventions) conventions. 


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
