from rest_framework import serializers

from payments.models import Transactions

class TransactionSerializer(serializers.Serializer):

  class Meta:
    model = Transactions
    fields = ['id', 'transaction_id', 'type', 'transaction_time', 'transaction_amount', 
    'mpesa_receipt_number', 'status', 'description']
    read_only_fields = 


