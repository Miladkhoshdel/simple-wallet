from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from wallets.models import Wallet
from unittest.mock import patch

class WalletViewTest(TestCase):
    """
    Test class for WalletViews.

    This class contains test methods for testing the Wallet Views functionality,
    including retrieving wallet details, creating deposits, and creating withdrawals.
    """
    def setUp(self):
        """
        Set up the test environment.

        This method is called before each test method execution.
        It sets up the test client and creates a wallet with an initial balance of 200.00.
        """
        self.client = APIClient()
        self.wallet = Wallet.objects.create(balance=200.00)

    def test_retrieve_wallet(self):
        """
        Test retrieving wallet details.

        This method tests the functionality of retrieving wallet details by sending
        a GET request to the 'retrieve_wallet' endpoint and asserting the returned
        response's status code and balance value.

        Steps:
        1. Generate the URL for retrieving wallet details.
        2. Send a GET request to the generated URL.
        3. Verify that the response status code is 200 (OK).
        4. Verify that the returned balance matches the expected value.

        """
        url = reverse('wallets:retrieve_wallet', kwargs={'uuid': self.wallet.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '200.00')

    def test_create_deposit(self):
        """
        Test creating a deposit.

        This method tests the functionality of creating a deposit into a wallet by
        sending a POST request to the 'create_deposit' endpoint with a specified
        deposit amount. It verifies that the deposit is successful and the new balance
        matches the expected value.

        Steps:
        1. Generate the URL for creating a deposit.
        2. Prepare data for the deposit, including the deposit amount.
        3. Send a POST request to the generated URL with the deposit data.
        4. Verify that the response status code is 200 (OK).
        5. Verify that the returned new balance matches the expected value after deposit.

        """
        url = reverse('wallets:create_deposit', kwargs={'uuid': self.wallet.uuid})
        data = {'amount': 50.0}  # Deposit amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['new_balance'], 250.00)

    def test_create_deposit_zero(self):
        """
        Test creating a deposit with zero amount.

        This method tests the behavior of the 'create_deposit' endpoint when attempting
        to deposit zero amount into a wallet. It sends a POST request with an amount
        of zero and verifies that the request is rejected with a status code of 400 (Bad Request).

        Steps:
        1. Generate the URL for creating a deposit.
        2. Prepare data for the deposit with zero amount.
        3. Send a POST request to the generated URL with the deposit data.
        4. Verify that the response status code is 400 (Bad Request), indicating rejection.

        """
        url = reverse('wallets:create_deposit', kwargs={'uuid': self.wallet.uuid})
        data = {'amount': 0}  # Deposit amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_deposit_negative(self):
        """
        Test creating a deposit with a negative amount.

        This method tests the behavior of the 'create_deposit' endpoint when attempting
        to deposit a negative amount into a wallet. It sends a POST request with a negative
        amount and verifies that the request is rejected with a status code of 400 (Bad Request).

        Steps:
        1. Generate the URL for creating a deposit.
        2. Prepare data for the deposit with a negative amount.
        3. Send a POST request to the generated URL with the deposit data.
        4. Verify that the response status code is 400 (Bad Request), indicating rejection.

        """
        url = reverse('wallets:create_deposit', kwargs={'uuid': self.wallet.uuid})
        data = {'amount': -1}  # Deposit amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('wallets.models.requests.post')
    def test_create_withdraw_bank_service_success(self, mock_post):
        """
        Test successful withdrawal with bank service integration.

        This method tests the functionality of creating a withdrawal from a wallet
        using the 'create_withdraw' endpoint. It mocks the external bank service's
        response to simulate a successful withdrawal, verifies the HTTP response status
        code, and checks if the new balance matches the expected value.

        Steps:
        1. Patch the external bank service's POST method to return a mock response.
        2. Configure the mock response to simulate a successful withdrawal.
        3. Generate the URL for creating a withdrawal.
        4. Prepare data for the withdrawal, including the withdrawal amount.
        5. Send a POST request to the generated URL with the withdrawal data.
        6. Verify that the response status code is 200 (OK).
        7. Verify that the returned new balance matches the expected value after withdrawal.

        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 200, 'data': 'success'}

        url = reverse('wallets:create_withdraw', kwargs={'uuid': self.wallet.uuid})
        data = {'amount': 50.0}  # Deposit amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['new_balance'], 150.00)


    @patch('wallets.models.requests.post')
    def test_create_withdraw_bank_service_error(self, mock_post):
        """
        Test withdrawal failure with bank service integration.

        This method tests the behavior of the 'create_withdraw' endpoint when a withdrawal
        request fails due to an error from the external bank service. It mocks the external
        bank service's response to simulate a withdrawal failure, verifies the HTTP response
        status code, and checks if the wallet balance remains unchanged.

        Steps:
        1. Patch the external bank service's POST method to return a mock response.
        2. Configure the mock response to simulate a withdrawal failure.
        3. Generate the URL for creating a withdrawal.
        4. Prepare data for the withdrawal, including the withdrawal amount.
        5. Send a POST request to the generated URL with the withdrawal data.
        6. Verify that the response status code is 200 (OK) as the endpoint handles the error gracefully.
        7. Verify that the wallet balance remains unchanged (equal to 200.00) after the withdrawal failure.

        """
        mock_post.return_value.status_code = 503
        mock_post.return_value.json.return_value = {'status': 503, 'data': 'failed'}

        url = reverse('wallets:create_withdraw', kwargs={'uuid': self.wallet.uuid})
        data = {'amount': 50.0}  # Deposit amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['new_balance'], 200.00)

    def test_create_withdraw_zero(self):
        """
        Test creating a withdrawal with zero amount.

        This method tests the behavior of the 'create_withdraw' endpoint when attempting
        to withdraw zero amount from a wallet. It sends a POST request with an amount
        of zero and verifies that the request is rejected with a status code of 400 (Bad Request).

        Steps:
        1. Generate the URL for creating a withdrawal.
        2. Prepare data for the withdrawal with zero amount.
        3. Send a POST request to the generated URL with the withdrawal data.
        4. Verify that the response status code is 400 (Bad Request), indicating rejection.

        """
        url = reverse('wallets:create_withdraw', kwargs={'uuid': self.wallet.uuid})
        data = {'amount': 0}  # Deposit amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_withdraw_negative(self):
        """
        Test creating a withdrawal with a negative amount.

        This method tests the behavior of the 'create_withdraw' endpoint when attempting
        to withdraw a negative amount from a wallet. It sends a POST request with a negative
        amount and verifies that the request is rejected with a status code of 400 (Bad Request).

        Steps:
        1. Generate the URL for creating a withdrawal.
        2. Prepare data for the withdrawal with a negative amount.
        3. Send a POST request to the generated URL with the withdrawal data.
        4. Verify that the response status code is 400 (Bad Request), indicating rejection.

        """
        url = reverse('wallets:create_withdraw', kwargs={'uuid': self.wallet.uuid})
        data = {'amount': -1}  # Deposit amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_withdraw_insufficient_balance(self):
        """
        Test creating a withdrawal with insufficient balance.

        This method tests the behavior of the 'create_withdraw' endpoint when attempting
        to withdraw an amount larger than the wallet's balance. It sends a POST request
        with an amount exceeding the wallet balance and verifies that the request is
        rejected with a status code of 402 (Payment Required).

        Steps:
        1. Generate the URL for creating a withdrawal.
        2. Prepare data for the withdrawal with an amount exceeding the wallet balance.
        3. Send a POST request to the generated URL with the withdrawal data.
        4. Verify that the response status code is 402 (Payment Required), indicating
        insufficient balance for the withdrawal.

        """
        url = reverse('wallets:create_withdraw', kwargs={'uuid': self.wallet.uuid})
        data = {'amount': 1000}  # Deposit amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
