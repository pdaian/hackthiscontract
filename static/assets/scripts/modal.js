function showModal(challenge_name) {
    console.info("Show");
    var modal = document.getElementById(challenge_name);
    console.info(modal);
    modal.style.display = "block";
}

function hideModal(challenge_name) {
    console.info("Hide");
    var modal = document.getElementById(challenge_name);
    modal.style.display = "none";
}