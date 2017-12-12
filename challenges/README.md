# Adding new contracts
1. Put the contract in a .sol file in this directory (name must be ##_contract_name.ending)
2. Create a JSON file describing the contract
3. Create a Python file which checks whether the contract has been hacked 

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
| level         | Difficulty on a scale of 1 to 10                    | Yes      |


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
The class **must** be called `Contract`, **must** extend `IContract` and **must** implement all methods.
`has_been_hacked` **must** return `True` if the contact has been hacked, `False` otherwise.
`setup` is optional, though the method **must** be overwritten.

### Variables
The Contract will have the following variables already set: 

| Name             | Description                            |
| ---------------- | -------------------------------------- |
| contract_address | The address the contract is located at |
| user_address     | The address of the user                |
| web3             | An instance of EasyWeb3                |