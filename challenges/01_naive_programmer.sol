pragma solidity ^0.4.7;

contract SourceTrixAreForl337 {
    // The two choices for your vote
    string public choice1;
    string public choice2;

    // Information about the current status of the vote
    uint public votesForChoice1;
    uint public votesForChoice2;
    uint public commitPhaseEndTime;
    uint public numberOfVotesCast = 0;

    // The actual votes and vote commits
    bytes32[] public voteCommits;
    mapping(bytes32 => string) voteStatuses; // Either `Committed` or `Revealed`

    // Events used to log what's going on in the contract
    event logString(string);
    event newVoteCommit(string, bytes32);
    event voteWinner(string, string);

    // Constructor used to set parameters for the this specific vote
    function SourceTrixAreFor1337(uint _commitPhaseLengthInSeconds, 
                                  string _choice1, 
                                  string _choice2) {
        if (_commitPhaseLengthInSeconds < 20) {
            throw;
        }
        commitPhaseEndTime = now + _commitPhaseLengthInSeconds * 1 seconds;
        choice1 = _choice1;
        choice2 = _choice2;
    }

    function commitVote(bytes32 _voteCommit) {
        if (now > commitPhaseEndTime) throw; // Only allow commits during committing period

        // Check if this commit has been used before
        bytes memory bytesVoteCommit = bytes(voteStatuses[_voteCommit]);
        if (bytesVoteCommit.length != 0) throw;

        // We are still in the committing period & the commit is new so add it
        voteCommits.push(_voteCommit);
        voteStatuses[_voteCommit] = "Committed";
        numberOfVotesCast ++;
        newVoteCommit("Vote committed with the following hash:", _voteCommit);
    }

    function revealVote(string _vote, bytes32 _voteCommit) {
        if (now < commitPhaseEndTime) throw; // Only reveal votes after committing period is over

        // FIRST: Verify the vote & commit is valid
        bytes memory bytesVoteStatus = bytes(voteStatuses[_voteCommit]);
        if (bytesVoteStatus.length == 0) {
            logString('A vote with this voteCommit was not cast');
        } else if (bytesVoteStatus[0] != 'C') {
            logString('This vote was already cast');
            return;
        }

        if (_voteCommit != keccak256(_vote)) {
            logString('Vote hash does not match vote commit');
            return;
        }

        // NEXT: Count the vote!
        bytes memory bytesVote = bytes(_vote);
        if (bytesVote[0] == '1') {
            votesForChoice1 = votesForChoice1 + 1;
            logString('Vote for choice 1 counted.');
        } else if (bytesVote[0] == '2') {
            votesForChoice2 = votesForChoice2 + 1;
            logString('Vote for choice 2 counted.');
        } else {
            logString('Vote could not be read! Votes must start with the ASCII character `1` or `2`');
        }
        voteStatuses[_voteCommit] = "Revealed";
    }

    function getWinner () constant returns(string) {
        // Only get winner after all vote commits are in
        if (now < commitPhaseEndTime) throw;
        // Make sure all the votes have been counted
        if (votesForChoice1 + votesForChoice2 != voteCommits.length) throw;

        if (votesForChoice1 > votesForChoice2) {
            voteWinner("And the winner of the vote is:", choice1);
            return choice1;
        } else if (votesForChoice2 > votesForChoice1) {
            voteWinner("And the winner of the vote is:", choice2);
            return choice2;
        } else if (votesForChoice1 == votesForChoice2) {
            voteWinner("The vote ended in a tie!", "");
            return "It was a tie!";
        }
    }
}
