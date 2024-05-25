# Wallet Service
This is a simple wallet project with deposit/withdraw and scheduled withdraw capabilities. To prevent floating-point arithmetic errors, the balance data structure is set to decimal.

### technologies
- Django
- DRF
- Celery
- Celery beat
- RabbitMQ

## Installation
- Clone the project
- Create your virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```
- Install requirements:
```
pip install -r requirments.txt
```
- Run the following commands to create the database:
```
python manage.py makemigrations
python manage.py migrate
```
- Create a user:
```
python manage.py createsuperuser
```
- Run the project:
```
python manage.py runserver {IP}:{PORT}
```
- Run celery and celery beat workers:
```
celery -A wallet beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
celery -A wallet worker --loglevel=info --concurrency {NUMBER-OF-WORKERS:INT} -E -Q withdraw
```
- Run test (Optional)
```
python manage.py test
```
## Create Wallet
This API is used to create a wallet. You can set the initial balance, but the UUID field is optional, and the system will generate it if you do not provide it.

Sample Request:
```
POST /wallets/

{
    "uuid": ""
    "balance": {int}
}
```
Sample response:
```
HTTP 201 Created
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "id": 6,
    "created_at": "2024-05-25T05:33:39.261297Z",
    "updated_at": "2024-05-25T05:33:39.261394Z",
    "uuid": "12c599be-7847-47d4-b063-e80e6e36b0cb",
    "balance": "0.00"
}
```
## Retrieve Wallet
This API is used to retrieve a specific wallet.

Sample Request:
```
GET /wallets/12c599be-7847-47d4-b063-e80e6e36b0cb/
```
Sample response:
```
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "id": 6,
    "created_at": "2024-05-25T05:33:39.261297Z",
    "updated_at": "2024-05-25T05:33:39.261394Z",
    "uuid": "12c599be-7847-47d4-b063-e80e6e36b0cb",
    "balance": "0.00"
}
```
## Deposit API
This API is used to deposit into your account. The amount should be a positive number.

Sample Request:
```
POST /wallets/12c599be-7847-47d4-b063-e80e6e36b0cb/deposit

{
"amount": 1000
}
```
Sample response:
```
HTTP 200 OK
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "uuid": "12c599be-7847-47d4-b063-e80e6e36b0cb",
    "new_balance": 1000.25
}
```

## Withdraw API
This API is used to withdraw from your account. It sends a withdrawal request to the bank. If it receives a 200 response, the process will be completed successfully. The result will be logged in the Transaction model. You must have the amount in your account balance already. The amount should be a positive number.

Sample Request:
```
POST /wallets/12c599be-7847-47d4-b063-e80e6e36b0cb/withdraw

{
"amount": 1000
}
```
Sample response:
```
HTTP 200 OK
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "uuid": "12c599be-7847-47d4-b063-e80e6e36b0cb",
    "new_balance": 0.25
}
```
## Schedule Withdraw API
This API is used to schedule a withdrawal from your account. It freezes the transaction amount in your account until the due date. It sends a withdrawal request to the bank at the scheduled time. If it receives a 200 response, the process will be completed successfully. The scheduled time must be in the future, and you should already have the balance in your account.

It sends the task to Celery Beat on withdraw queue, and on the due date, Celery runs the task. The result will be logged in the Transaction model.

Sample Request:
```
POST /wallets/12c599be-7847-47d4-b063-e80e6e36b0cb/schedulewithdraw

{
    "amount":1,
    "scheduled_time":"2024-05-27 09:00:00"
}
```
Sample response:
```
HTTP 200 OK
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "status": "success",
    "message": "Withdrawal scheduled"
}
```
## Transactions
Transactions are submitted with messages and statuses received from the bank microservice for withdrawal processes. For scheduled withdrawal processes, the amount will be subtracted from the account balance. If the withdrawal process fails, the amount will be added back to the balance. This information is logged in the transaction model, as shown in the image below.

![GitHub Logo](/images/transactions.png)

## Variables
All required variables are stored in base/vars.py. This file should be moved into the Docker variable file for production.
Also the site key is generated randomly the first time the Django server is run."