# Adding New Challenges

## Overview and Steps

1. Write some solidity file that contains a vulnerability. Put the contract in a .sol file in the challenges directory (name must be `##_contract_name.sol`).
2. Create a JSON file describing the contract (`##_contract_name.json`)
3. Compile the contract using solc, put the abi in a file called `##_contract_name.abi` and the bytecode in a file called `##_contract_name.bin`
4. Create a Python file which checks whether the contract has been hacked (`##_contract_name.py`) - these are the graders.
5. Write a unit test to make sure the contract works (see `tests/test_challenges_public.py`)

## Writing Vulnerable Solidity Code 

Write some vulnerable solidity code.

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

## Compiling the Contract

You can use desktop solc or a JavaScript compiler to compile your contract. The output of the abi should be a valid JavaScript array, preferably minimized. The bytecode should be hex-encoded, with no leading "0x" value. See the challenges directory for reference.

## Create a Validator File

We have provided an `icontract` class for implementers to add their own graders. You will extend this class in order to add your grader/validator.

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
`setup` is optional, though the method **must** be overwritten. Setup is a useful function to have if you need to do any post deployment (constructor) steps.

*Note:* the deployment code at this time cannot handle constructors that take parameters (it tries to deploy the contract without passing any constructor parameters). If your code would normally have a parameter, you should instead set an owner variable in the constructor equal to msg.sender, and then have an additional setter function that you can call from the setup function to initialize the constructor state to the desired value.

### Variables
The iContract object will have the following useful variables set and accessible:

| Name             | Description                                                                    |
| ---------------- | ------------------------------------------------------------------------------ |
| `self.contract_address` |  The address the contract is located at |
| `self.contract_object` | A web3.contract object you can use to call functions on your contract. |
| `self.user_address` |  The end user address that you are grading for. |
| `self.eweb3` | A handle to the eweb3 object. You can use `eweb3._web3` to get a hold on the web3 object to send arbitrary web3 commands |


## Unit Testing

Unit tests can be found in the tests directory. When you write your contract, you should write a unit test to assure yourself and others that the contract works as expected, that one can actually hack the contract as intended, and that your validator works. To add a unit test you can refer to the `test_challenges_public.py` file. You will probably want to additionally test against a private network so that you can run the unit test without affecting state or waiting for things to confirm on the testnet. For that, we reocomment running geth as a development node. The command is as follows:

`/home/tyler/Documents/go/src/github.com/ethereum/go-ethereum/build/bin/geth --dev --rpc --rpcapi "admin,debug,miner,personal,txpool,web3,eth" --rpccorsdomain "*"`

You can then attach to the IPC node attaching to geth for manual instrospection of the chain or in python with web3.py:

`/home/tyler/Documents/go/src/github.com/ethereum/go-ethereum/build/bin/geth attach /tmp/geth.ipc`
