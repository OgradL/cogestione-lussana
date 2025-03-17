
async function send_comando() {
    let input = document.getElementById("comando");
	console.log(input.value);
	let comando = input.value;
	console.log(document.URL);
	const response = await fetch(document.URL, {
		method:"POST",
		headers:
			{"comando" : comando}
	});

	console.log(await response.headers)
	// console.log(await response.text())

	document.getElementById("result").innerText = await response.headers.get("result");

}

async function iscrizione(corso_id) {
	let url = "/iscrizione/";
	// console.log(document.URL, url);
	await fetch(url, {
		method: "POST",
		body: JSON.stringify({id_corso : corso_id})
	}).then((res) => {
		window.location.reload();
	});

	// console.log(response.status);
}

async function annulla_iscrizione(corso_id) {
	let url = "/annulla-iscrizione/";

	await fetch(url, {
		method: "POST",
		body: JSON.stringify({id_corso : corso_id})
	}).then((ret) => {
		window.location.reload();
	});
}

function del_flashed_message(message) {
	message.parentElement.remove();
}