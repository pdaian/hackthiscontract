# Adding new contracts
1. Put the contract in a .sol file in this directory (name must be `##_contract_name.sol`)
2. Compile the contract using solc, put the abi in a file called `##_contract_name.abi` and the bytecode in a file called `##_contract_name.bin`
3. Create a JSON file describing the contract
4. Create a Python file which checks whether the contract has been hacked 

## Writing a JSON descriptor
A JSON descriptor looks like this:
```json
{
    "name" : "Test",
    "description" : "A test.",
    "level" : "3"
}
```

| Key           | Description                                         | Required |
| ------------- | --------------------------------------------------- | -------- |
| name          | The name that will be displayed on the website      | Yes      |
| description   | The description to show on the website              | Yes      |
| level         | Difficulty on a scale of 1 to 5                     | Yes      |


## Writing a validator
A minimal validator looks like this:
```python
import icontract

class Contract(icontract.IContract):
    def setup(self, web3_contract):
        pass
        
    def has_been_hacked(self):
            return False
```
The class **must** be called `Contract`, **must** extend `IContract` and **must** implement methods `setup` and `has_been_hacked`.
`has_been_hacked` **must** return `True` if the contact has been hacked, `False` otherwise.
`setup` is optional, though the method **must** be overwritten.

### Variables
The iContract object will have the following useful variables set and accessible:

| Name             | Description                                                                    |
| ---------------- | ------------------------------------------------------------------------------ |
| `self.contract_address` |  The address the contract is located at |
| `self.contract_object` | A web3.contract object you can use to call functions on your contract. |
| `self.user_address` |  The end user address that you are grading for. |
| `self.eweb3` | A handle to the eweb3 object. You can use `eweb3._web3` to get a hold on the web3 object to send arbitrary web3 commands |
